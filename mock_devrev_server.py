import time
from fastapi import FastAPI, HTTPException, Header, Request, File, BackgroundTasks
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import json
import random
import copy
import gzip
import os
import asyncio
from datetime import datetime, timezone, timedelta


app = FastAPI()
# Avoid automatic trailing-slash redirects which can interact badly with streaming uploads
app.router.redirect_slashes = False

# Initialize application state containers
app.state.uploaded_states = {} # mapping sync_unit -> state object
app.state.uploaded_artifacts_length = {}  # mapping artifact_id -> content length
app.state.artifact_id_to_name = {} # mapping artifact_id -> artifact name (e.g. "cards", "attachments", ...)
app.state.artifact_contents = {} # mapping artifact_id -> decompressed artifact content)

class ArtifactPrepareRequest(BaseModel):
    file_name: str
    file_type: str

class FormDataField(BaseModel):
    key: str
    value: str

class ArtifactPrepareResponse(BaseModel):
    id: str
    url: str
    form_data: List[FormDataField]

class ExternalWorkerResponse(BaseModel):
    state: str

class AirdropArtifactResponse(BaseModel):
    artifact_id: str
    upload_url: str
    form_data: Dict[str, str]

@app.get("/is_uploaded/{artifact_id:path}")
async def was_artifact_uploaded(artifact_id: str):
    """Check if an artifact with the given artifact_id was uploaded"""
    # This endpoint is used for testing the attachments extraction worker.
    print(f"Received /is_uploaded/{artifact_id} GET request")
    if artifact_id in app.state.uploaded_artifacts_length:
        return {"artifact_id": artifact_id, "uploaded": True, "content_length": app.state.uploaded_artifacts_length[artifact_id]}
    raise HTTPException(status_code=404, detail="Artifact not found")

@app.post("/upload/{artifact_id:path}")
async def upload_artifact(
    artifact_id: str,
    file: bytes = File(...),
):
    # Here, we upload artifact metadata. The data is in "gibberish" form - encoded with gzip. Here, on the server, we decode this and store in the artifact contents dictionary.
    print(f"Received /upload/{artifact_id} POST request")
    try:
        content = file
        # decode the data on the mock server
        # example content variable: 
        # b'{"id":"68c04a0fc549efffaccb0300","url":"https://devrev.ai/","file_name":"devrev cover","parent_id":"688725db990240b77167efef","author_id":"6752eb529b14a3446b75e69c"}\n{"id":"68c2be83c413a1889bde83df","url":"https://trello.com/1/cards/688725db990240b77167efef/attachments/68c2be83c413a1889bde83df/download/2d7a71f4ebe27d165f5ea1974ca2bfbb529ad90d-1200x627.png","file_name":"2d7a71f4ebe27d165f5ea1974ca2bfbb529ad90d-1200x627.png","parent_id":"688725db990240b77167efef","author_id":"6752eb529b14a3446b75e69c"}'
        try:
            content = file.decode('utf-8').encode('latin-1')
        except (UnicodeDecodeError, UnicodeEncodeError):
            # If it fails, proceed with the original content, maybe it's not corrupted.
            pass
        # Decompress the content before storing
        decompressed_content = gzip.decompress(content)
        
        # Store the content length of the original uploaded file
        app.state.uploaded_artifacts_length[artifact_id] = len(file)
        # Store the decompressed content
        app.state.artifact_contents[artifact_id] = decompressed_content
        return {"status": "success", "message": "File uploaded successfully"}
    except Exception as e:
        print(f"Error uploading artifact: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/artifacts.prepare", response_model=ArtifactPrepareResponse)
async def prepare_artifact(
    request: ArtifactPrepareRequest,
    authorization: Optional[str] = Header(None)
):
    print("Received /artifacts.prepare POST request")
    # Generate a unique artifact ID
    artifact_id = str(uuid.uuid4())
    
    # Create a mock S3-like URL for the upload
    upload_url = f"http://localhost:8003/upload/{artifact_id}"
    
    # Create form data fields that would typically be required for S3 upload
    form_data = [
        FormDataField(key="key", value=f"artifacts/{artifact_id}/{request.file_name}"),
        FormDataField(key="Content-Type", value=request.file_type),
        FormDataField(key="x-amz-meta-artifact-id", value=artifact_id),
    ]
    
    return ArtifactPrepareResponse(
        id=artifact_id,
        url=upload_url,
        form_data=form_data
    )

@app.get("/external-worker.get-all-states")
async def get_all_external_worker_states():
    """Not called anywhere, for debugging/internal purposes"""
    print("Received /external-worker.get-all-states GET request")
    return app.state.uploaded_states

@app.get("/external-worker.get", response_model=ExternalWorkerResponse)
async def get_external_worker(sync_unit: str):
    print(f"Received /external-worker.get GET request for sync_unit: {sync_unit}")
    # Check if uploaded_states contains the specific sync_unit
    if sync_unit in app.state.uploaded_states:
        stored_state = app.state.uploaded_states[sync_unit]
        # If the stored state is already a string, return it directly
        # Otherwise, serialize it to JSON
        if isinstance(stored_state, str):
            return ExternalWorkerResponse(state=stored_state)
        else:
            return ExternalWorkerResponse(state=json.dumps(stored_state))
    else:
        print(f"No uploaded state found for sync_unit: {sync_unit}, returning 404")
        raise HTTPException(status_code=404, detail="State not found for sync_unit")

@app.post("/external-worker.update")
async def update_external_worker(sync_unit: str, request: Request):
    print(f"Received /external-worker.update POST request for sync_unit: {sync_unit}")
    body = await request.body()
    try:
        parsed = json.loads(body.decode("utf-8"))
        # If the parsed JSON has a 'state' field, use that as the state
        # Otherwise, use the entire parsed object as the state
        if 'state' in parsed:
            app.state.uploaded_states[sync_unit] = json.loads(parsed['state'])
        else:
            app.state.uploaded_states[sync_unit] = copy.deepcopy(json.loads(parsed))

        print(f"Updated state for sync_unit: {sync_unit}\n", json.dumps(app.state.uploaded_states[sync_unit], indent=4))
    except Exception as e:
        print("Failed to pretty print JSON:", e)
        print(body.decode("utf-8"))
    return {"status": "received"}

@app.post("/external-worker.update-last-successful-sync/{sync_unit}")
async def update_last_successful_sync(sync_unit: str, request: Request):
    """Update lastSuccessfulSyncStarted for a sync unit"""
    print(f"Received /external-worker.update-last-successful-sync POST request for sync_unit: {sync_unit}")
    # Set current time iso to a bit less than the current time (30 seconds), so we can test incremental mode with it.
    # current_time_iso = (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat()
    current_time_iso = datetime.now(timezone.utc).isoformat()
    print(f"Setting lastSuccessfulSyncStarted to: {current_time_iso}")

    body = await request.json()
    if "snap_in_version_id" not in body:
        raise HTTPException(status_code=400, detail="snap_in_version_id is required")

    if sync_unit not in app.state.uploaded_states:
        base_state = {
            "lastSyncStarted": "",
            "lastSuccessfulSyncStarted": current_time_iso,
            "snapInVersionId": body["snap_in_version_id"],
            "toDevRev": {
                "attachmentsMetadata": {
                    "artifactIds": [],
                    "lastProcessed": 0,
                    "lastProcessedAttachmentsIdsList": []
                }
            }
        }
        
        if "extend_state" in body:
            base_state.update(body["extend_state"])
            
        app.state.uploaded_states[sync_unit] = base_state

    app.state.uploaded_states[sync_unit]["lastSuccessfulSyncStarted"] = current_time_iso
    
    print(f"Updated state for sync_unit: {sync_unit}\n", json.dumps(app.state.uploaded_states[sync_unit], indent=4))
    return {"status": "success"}


@app.get("/internal/snap-ins.get")
async def get_snap_ins(request: Request):
    # auxiliary endpoint, intended just for testing to run smoothly.
    print("Received /internal/snap-ins.get GET request")
    return {
        "snap_in": {
            "imports": [{"name": "test_import_slug"}],
            "snap_in_version": {"slug": "test_snap_in_slug"}
        }
    }

@app.post("/internal/airdrop.recipe.initial-domain-mappings.install")
async def install_initial_domain_mappings():
    # auxiliary endpoint, intended just for testing to run smoothly.
    print("Received /internal/airdrop.recipe.initial-domain-mappings.install POST request")
    return {
        "success": True,
        "message": "Initial domain mappings installed successfully"
    }


@app.get("/internal/airdrop.artifacts.upload-url", response_model=AirdropArtifactResponse)
async def airdrop_artifacts_upload_url(
    file_type: str,
    file_name: str,
    request_id: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    print("Received /internal/airdrop.artifacts.upload-url GET request")

    if file_type == "application/x-gzip":
        # In this case, we're generating upload URL for any artifacts (e.g. users, cards, attachments, etc.)
        # file_name = "cards.jsonl.gz" -> strip json.gz away
        artifact_name = file_name.replace(".jsonl.gz", "")
        # Generate a unique artifact ID in the required format
        partition = "dvrv-us-1"
        devOrgID = "1"
        random_int = random.randint(1, 1000)
        artifact_id = f"don:core:{partition}:devo/{devOrgID}:artifact/{random_int}"
        # artifact_id = f"don:core:dvrv-us-1:devo/1:artifact/211"
        
        app.state.artifact_id_to_name[artifact_id] = artifact_name
        
        # Create a mock S3-like URL for the upload
        upload_url = f"http://localhost:8003/upload/{artifact_id}"
        
        # Create form data fields that would typically be required for S3 upload
        form_data = {
            "key": f"airdrop-artifacts/{artifact_id}/{file_name}",
            "Content-Type": file_type,
            "x-amz-meta-artifact-id": artifact_id,
        }
        
        return AirdropArtifactResponse(
            artifact_id=artifact_id,
            upload_url=upload_url,
            form_data=form_data
        )
    else:
        # from app.state.artifact_id_to_name, find the artifact_id where the key in this dictionary is "attachments"
        artifact_id = next((k for k, v in app.state.artifact_id_to_name.items() if v == "attachments"), None)
        if not artifact_id:
            # should not happen - at this point we already uploaded the attachment metadata artifact ID, and how we're streaming it.
            print("Attachments artifact not found. Current artifact_id_to_name:", app.state.artifact_id_to_name)
            raise HTTPException(status_code=400, detail="Attachments artifact not found")

        # The upload_url is different here, because it's not gzipped.
        # This will be handled by the stream_artifact endpoint
        upload_url = f"http://localhost:8003/stream_artifact/{artifact_id}"
        
        form_data = {
            "key": f"streaming-attachments/{artifact_id}/{file_name}",
            "Content-Type": file_type,
            "x-amz-meta-artifact-id": artifact_id,
        }

        return AirdropArtifactResponse(
            artifact_id=artifact_id,
            upload_url=upload_url,
            form_data=form_data
        )

async def process_stream_in_background(request: Request, artifact_id: str):
    """
    This function runs in the background. It attempts to read the stream,
    but even if it hangs, the client has already received its 200 OK.
    """
    print(f"BG Task: Starting to process stream for artifact {artifact_id}.")
    actual_length = 0
    try:
        # We still use a timeout here as a defensive measure for the background task itself.
        stream_iterator = request.stream().__aiter__()
        while True:
            chunk = await asyncio.wait_for(stream_iterator.__anext__(), timeout=5.0)
            actual_length += len(chunk)
    except StopAsyncIteration:
        print(f"BG Task: Stream for {artifact_id} finished normally.")
    except asyncio.TimeoutError:
        print(f"BG Task: Stream for {artifact_id} timed out; assuming complete.")
    except Exception as e:
        print(f"BG Task: An error occurred processing stream for {artifact_id}: {e}")

    if actual_length > 0:
        app.state.uploaded_artifacts_length[artifact_id] = actual_length
        print(f"BG Task: Successfully streamed artifact {artifact_id} with size {actual_length} bytes.")
    else:
        print(f"BG Task: No data was read for artifact {artifact_id}.")


@app.post("/stream_artifact/{artifact_id:path}")
async def stream_artifact(
    artifact_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    This endpoint immediately returns a 200 OK and schedules the actual
    stream processing to happen in the background. This breaks the deadlock.
    """
    print(f"Received /stream_artifact/{artifact_id} POST request. Scheduling background processing and returning 200 OK immediately.")
    background_tasks.add_task(process_stream_in_background, request, artifact_id)
    return {"status": "success", "message": "File streaming acknowledged."}

@app.post("/internal/airdrop.artifacts.confirm-upload")
async def confirm_upload(request: Request):
    print("Received /internal/airdrop.artifacts.confirm-upload POST request")
    try:
        body = await request.json()
        print("Received /internal/airdrop.artifacts.confirm-upload POST body:")
        print(json.dumps(body, indent=2))
    except Exception as e:
        print("Could not parse JSON from /internal/airdrop.artifacts.confirm-upload request body:", e)

    return {"status": "success"}

@app.post("/reset-mock-server")
async def reset_mock_server():
    """Reset the mock server state by clearing uploaded_states, uploaded_artifacts and artifact_id_to_name"""
    app.state.uploaded_states = {}
    app.state.uploaded_artifacts_length = {}
    app.state.artifact_id_to_name = {}
    app.state.artifact_contents = {}
    print("Server state reset - uploaded_states, uploaded_artifacts, artifact_id_to_name and artifact_contents cleared")
    return {"status": "success", "message": "Mock server state reset successfully"}

@app.get("/internal/airdrop.artifacts.download-url")
async def airdrop_artifacts_download_url(
    artifact_id: str,
    request_id: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    """Mock endpoint to get artifact download URL"""
    print(f"Received /internal/airdrop.artifacts.download-url GET request for artifact_id: {artifact_id}, request_id: {request_id}")
    return {
        "download_url": f"http://localhost:8003/download/{artifact_id}.jsonl.gz"
    }

@app.get("/download/{file_name:path}")
async def download_jsonl_gz_file(file_name: str):
    """Endpoint to serve .jsonl.gz files for Node.js download"""
    print(f"Received download request for file: {file_name}")
    
    if not file_name.endswith('.jsonl.gz'):
        raise HTTPException(status_code=400, detail="Only .jsonl.gz files are supported")

    artifact_id = file_name.replace(".jsonl.gz", "")

    # this content is decompressed, we need to compress it back
    decompressed_content = app.state.artifact_contents[artifact_id]

    # Compress the content using gzip
    artifact_content = gzip.compress(decompressed_content)

    # get artifact name from the state
    artifact_name = app.state.artifact_id_to_name[artifact_id]
    # file_name should be artifact_name-unix-timestamp.jsonl.gz
    output_file_name = f"{artifact_name}-{int(time.time())}.jsonl.gz"
    
    # Debug: Print compression info
    print(f"Decompressed content length: {len(decompressed_content)}")
    print(f"Compressed content length: {len(artifact_content)}")
    
    return Response(
        content=artifact_content,
        media_type="application/gzip",
        headers={
            "Content-Disposition": f"attachment; filename={output_file_name}",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8003)
