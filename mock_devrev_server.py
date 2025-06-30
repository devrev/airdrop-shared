from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import json

app = FastAPI()

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
    form_data: List[FormDataField]

@app.post("/upload/{artifact_id}")
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
async def get_external_worker():
    print("Received /external-worker.get GET body:")
    state = {
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
    return ExternalWorkerResponse(state=json.dumps(state))

@app.post("/external-worker.update")
async def update_external_worker(request: Request):
    body = await request.body()
    print("Received /external-worker.update POST body:")
    try:
        parsed = json.loads(body.decode("utf-8"))
        print(json.dumps(parsed, indent=2))
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
    # Generate a unique artifact ID
    artifact_id = str(uuid.uuid4())
    
    # Create a mock S3-like URL for the upload
    upload_url = f"http://localhost:8003/upload/{artifact_id}"
    
    # Create form data fields that would typically be required for S3 upload
    form_data = [
        FormDataField(key="key", value=f"airdrop-artifacts/{artifact_id}/{file_name}"),
        FormDataField(key="Content-Type", value=file_type),
        FormDataField(key="x-amz-meta-artifact-id", value=artifact_id),
    ]
    
    return AirdropArtifactResponse(
        artifact_id=artifact_id,
        upload_url=upload_url,
        form_data=form_data
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8003)
