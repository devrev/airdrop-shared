# This proxy server requires 'fastapi', 'uvicorn', and 'httpx'.
# You can install them with: pip install fastapi uvicorn httpx

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, Response, StreamingResponse
import httpx
import datetime
import email.utils
import os
from pydantic import BaseModel
import logging

app = FastAPI()

# Create a single, long-lived client instance for connection pooling
client = httpx.AsyncClient(timeout=30.0)


from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await client.aclose()

app = FastAPI(lifespan=lifespan)

# In-memory state for rate limiting
app.state.rate_limiting_active = False
app.state.test_name = ""

# The API URL to which requests will be proxied.
# Configurable via the PROXY_API_URL environment variable.
API_URL = os.getenv("PROXY_API_URL")
if not API_URL:
    print("Error: PROXY_API_URL environment variable not set")
    exit(69)  # EXIT_SERVICE_UNAVAILABLE

if not API_URL.endswith("/"):
    print("Error: PROXY_API_URL environment variable must end with a slash. Current API URL: ", API_URL)
    exit(69)  # EXIT_SERVICE_UNAVAILABLE

RATE_LIMIT_DELAY = 3


def is_streaming_response(response: httpx.Response) -> bool:
    """Check if the response should be streamed."""
    # 1. The server is explicitly streaming the response.
    if response.headers.get('transfer-encoding', '').lower() == 'chunked':
        return True

    # 2. The response content suggests it should be streamed.
    content_type = response.headers.get('content-type', '').lower()
    content_disposition = response.headers.get('content-disposition', '').lower()

    # Stream if it's a file attachment
    if 'attachment' in content_disposition:
        return True

    # Stream if it's a common large file type
    if content_type.startswith((
            'application/octet-stream', 'application/pdf', 'application/zip',
            'image/', 'video/', 'audio/'
    )):
        return True

    # Stream if the content length is over a certain threshold (e.g., 1MB)
    content_length = int(response.headers.get('content-length', 0))
    if content_length > 1024 * 1024:
        return True

    return False


class RateLimitStartRequest(BaseModel):
    test_name: str


@app.post("/start_rate_limiting")
async def start_rate_limiting(request_body: RateLimitStartRequest):
    """Starts rate limiting all proxied requests."""
    app.state.rate_limiting_active = True
    app.state.test_name = request_body.test_name
    print(f"Rate limiting started for test: {app.state.test_name}")
    return JSONResponse(content={"status": f"rate limiting started for test: {app.state.test_name}"})


@app.post("/end_rate_limiting")
async def end_rate_limiting():
    """Ends rate limiting all proxied requests."""
    app.state.rate_limiting_active = False
    app.state.test_name = ""
    print(f"Rate limiting state ended")
    return JSONResponse(content={"status": "rate limiting ended"})


# Catch-all for proxying
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy(request: Request, path: str):
    """
    Proxies all incoming requests to the API_URL.
    If rate limiting is active, it returns a 429 status code.
    """
    if app.state.rate_limiting_active:
        retry_after_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=RATE_LIMIT_DELAY)
        retry_after_str = email.utils.formatdate(
            timeval=retry_after_time.timestamp(),
            localtime=False,
            usegmt=True
        )
        print(f"Rate limit exceeded for test {app.state.test_name}. Returning 429.")
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
            headers={"Retry-After": retry_after_str}
        )

    url = httpx.URL(API_URL).join(path)

    # Pass through headers from the original request, excluding the host header.
    headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}

    try:
        print(f"Received request on The API: {request.method} {url}")

        # Stream the request body to the upstream server
        req = client.build_request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.query_params,
            content=request.stream()
        )

        # Stream the response from the upstream server
        resp = await client.send(req, stream=True)

        if is_streaming_response(resp):
            print("Decision: streaming response")
            async def safe_iterator(response):
                try:
                    async for chunk in response.aiter_raw():
                        yield chunk
                except httpx.ReadError as e:
                    print(f"Upstream read error while streaming response: {e}")
                finally:
                    await response.aclose()

            return StreamingResponse(
                safe_iterator(resp),
                status_code=resp.status_code,
                headers=resp.headers,
            )
        else:
            print("Decision: buffering response")
            await resp.aread()
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=resp.headers,
            )
    except httpx.RequestError as exc:
        print(f"Error connecting to upstream server: {exc}\n{repr(exc)}")
        raise HTTPException(status_code=502, detail=f"Error connecting to upstream server: {exc}")


if __name__ == "__main__":
    import uvicorn
    print("Starting The API Server")
    uvicorn.run(app, host="localhost", port=8004)
