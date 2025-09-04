from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import json
import random
import copy

app = FastAPI()

# Initialize application state containers
app.state.uploaded_states = {}
app.state.uploaded_artifacts = {}  # Changed from set to dict to store content length

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
    if artifact_id in app.state.uploaded_artifacts:
        content_length = app.state.uploaded_artifacts[artifact_id]
        return {"artifact_id": artifact_id, "uploaded": True, "content_length": content_length}
    raise HTTPException(status_code=404, detail="Artifact not found")

@app.post("/upload/{artifact_id:path}")
async def upload_artifact(
    artifact_id: str,
    request: Request,
):
    try:
        # Read the raw body content
        content = await request.body()
        
        print(f"Received file upload with ID: {artifact_id}")
        print(f"Content length: {len(content)}")
        print(f"Content type: {request.headers.get('content-type', 'unknown')}")
        
        # Remember that this artifact_id was uploaded with its content length
        app.state.uploaded_artifacts[artifact_id] = len(content)
        
        return {"status": "success", "message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/artifacts.prepare", response_model=ArtifactPrepareResponse)
async def prepare_artifact(
    request: ArtifactPrepareRequest,
    authorization: Optional[str] = Header(None)
):
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

@app.get("/external-worker.get", response_model=ExternalWorkerResponse)
async def get_external_worker(sync_unit: str):
    print(f"Received /external-worker.get GET request for sync_unit: {sync_unit}")
    
    # Default state
    default_state = {
        "lastSyncStarted": "2024-06-01T12:00:00Z",
        "toDevRev": {
            "attachmentsMetadata": {
                "artifactIds": [],
                "lastProcessed": 0
            }
        },
        "test-artifact-1": {
            "completed": True,
            "offset": 0
        },
        "test-artifact-2": {
            "completed": True,
            "offset": 0
        }
    }

    default_state = {}

    # Check if uploaded_states contains the specific sync_unit
    if sync_unit in app.state.uploaded_states:
        print(f"Found uploaded state for sync_unit: {sync_unit}")
        stored_state = app.state.uploaded_states[sync_unit]
        # If the stored state is already a string, return it directly
        # Otherwise, serialize it to JSON
        if isinstance(stored_state, str):
            return ExternalWorkerResponse(state=stored_state)
        else:
            return ExternalWorkerResponse(state=json.dumps(stored_state))
    else:
        print(f"No uploaded state found for sync_unit: {sync_unit}, returning default state")
        return ExternalWorkerResponse(state=json.dumps(default_state))

@app.post("/external-worker.update")
async def update_external_worker(sync_unit: str, request: Request):
    body = await request.body()
    print(f"Received /external-worker.update POST request for sync_unit: {sync_unit}")
    try:
        parsed = json.loads(body.decode("utf-8"))
        # If the parsed JSON has a 'state' field, use that as the state
        # Otherwise, use the entire parsed object as the state
        if 'state' in parsed:
            app.state.uploaded_states[sync_unit] = parsed['state']
        else:
            app.state.uploaded_states[sync_unit] = copy.deepcopy(parsed)
        print(f"Stored state for sync_unit: {sync_unit}")
        print(json.dumps(app.state.uploaded_states[sync_unit], indent=2))
    except Exception as e:
        print("Failed to pretty print JSON:", e)
        print(body.decode("utf-8"))
    return {"status": "received"}

@app.get("/internal/snap-ins.get")
async def get_snap_ins(request: Request):
    print("Received /internal/snap-ins.get GET request")
    return {"status": "success"}

@app.get("/internal/airdrop.artifacts.upload-url", response_model=AirdropArtifactResponse)
async def airdrop_artifacts_upload_url(
    file_type: str,
    file_name: str,
    request_id: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    # Generate a unique artifact ID in the required format
    partition = "dvrv-us-1"
    devOrgID = "1"
    random_int = random.randint(1, 1000)
    artifact_id = f"don:core:{partition}:devo/{devOrgID}:artifact/{random_int}"
    
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

@app.post("/internal/airdrop.artifacts.confirm-upload")
async def confirm_upload(request: Request):
    try:
        body = await request.json()
        print("Received /internal/airdrop.artifacts.confirm-upload POST body:")
        print(json.dumps(body, indent=2))
    except Exception as e:
        print("Could not parse JSON from /internal/airdrop.artifacts.confirm-upload request body:", e)

    return {"status": "success"}

@app.post("/reset-mock-server")
async def reset_mock_server():
    """Reset the mock server state by clearing uploaded_states and uploaded_artifacts"""
    app.state.uploaded_states = {}
    app.state.uploaded_artifacts = {}
    print("Mock server state reset - uploaded_states and uploaded_artifacts cleared")
    return {"status": "success", "message": "Mock server state reset successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8003)
