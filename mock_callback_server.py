#!/usr/bin/env python3
from fastapi import FastAPI, Request
from datetime import datetime
import json
import uvicorn
import argparse

app = FastAPI()

async def log_request_details(request: Request, body: str):
    # Get request headers
    headers = dict(request.headers)
    client_host = request.client.host
    client_port = request.client.port
    
    # Log request details
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n{'='*50}")
    print(f"[{timestamp}] {request.method} {request.url.path}")
    print(f"\nReceived {request.method} request from {client_host}:{client_port}")
    print("\nHeaders:")
    print(json.dumps(headers, indent=2))
    print("\nBody:")
    try:
        # Try to pretty print if JSON
        parsed_body = json.loads(body)
        print(json.dumps(parsed_body, indent=2))
    except:
        print(body)
    print(f"{'='*50}\n")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Read and store the body
    body = await request.body()
    body_str = body.decode('utf-8')
    
    # Log the request details
    await log_request_details(request, body_str)
    
    # Create a new request with the same body
    response = await call_next(request)
    return response

@app.get("/{path:path}")
@app.post("/{path:path}")
@app.put("/{path:path}")
@app.delete("/{path:path}")
async def handle_request(request: Request):
    return {
        "status": "success",
        "message": "Request received"
    }

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run FastAPI server with optional port specification')
    parser.add_argument('--port', type=int, default=8001, help='Port number to run the server on (default: 8001)')
    args = parser.parse_args()

    print(f"Starting server on http://localhost:{args.port}")
    print("Use Ctrl+C to stop the server")
    print("\nServer is ready to accept requests...")
    uvicorn.run(app, host="localhost", port=args.port) 