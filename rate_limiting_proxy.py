import socket
import threading
import socketserver
import time
import sys
import ssl
import json
import datetime
import email.utils
from urllib.parse import urlparse

# Rate limiting settings
TOKEN_BUCKET_CAPACITY = 100  # requests
REFILL_RATE = 10  # requests per second
RATE_LIMIT_DELAY = 3 # seconds

class RateLimiterState:
    """A thread-safe class to manage the global rate limiting state."""
    def __init__(self):
        self.lock = threading.Lock()
        self.rate_limiting_active = False
        self.test_name = None

    def start_rate_limiting(self, test_name):
        with self.lock:
            self.rate_limiting_active = True
            self.test_name = test_name

    def end_rate_limiting(self):
        with self.lock:
            self.rate_limiting_active = False
            self.test_name = None

    def is_rate_limiting_active(self):
        with self.lock:
            return self.rate_limiting_active, self.test_name

rate_limiter_state = RateLimiterState()

class TokenBucket:
    """A thread-safe token bucket for rate limiting."""
    def __init__(self, capacity, refill_rate):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens):
        """Consumes tokens from the bucket. Returns True if successful, False otherwise."""
        with self.lock:
            now = time.time()
            time_since_refill = now - self.last_refill
            new_tokens = time_since_refill * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

rate_limiter = TokenBucket(TOKEN_BUCKET_CAPACITY, REFILL_RATE)

class ProxyHandler(socketserver.BaseRequestHandler):
    """Handles incoming proxy requests."""
    def handle(self):
        if not rate_limiter.consume(1):
            print("Rate limit exceeded. Dropping connection.")
            try:
                self.request.sendall(b'HTTP/1.1 429 Too Many Requests\r\n\r\n')
            except OSError:
                pass # Client might have already closed the connection.
            finally:
                self.request.close()
            return

        try:
            data = self.request.recv(4096)
        except ConnectionResetError:
            return  # Client closed connection.
        
        if not data:
            return

        first_line = data.split(b'\r\n')[0]
        try:
            method, target, _ = first_line.split()
        except ValueError:
            print(f"Could not parse request: {first_line}")
            self.request.close()
            return

        print(f"Received request: {method.decode('utf-8')} {target.decode('utf-8')}")

        path = target.decode('utf-8')
        # Check for control plane endpoints on the proxy itself
        if path.startswith(('/start_rate_limiting', '/end_rate_limiting')):
            self.handle_control_request(method, path, data)
            return

        # Check if global rate limiting is active
        is_active, test_name = rate_limiter_state.is_rate_limiting_active()
        if is_active:
            print(f"Rate limiting is active for test: '{test_name}'. Blocking request.")
            
            retry_after_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=RATE_LIMIT_DELAY)
            retry_after_str = email.utils.formatdate(
                timeval=retry_after_time.timestamp(),
                localtime=False,
                usegmt=True
            )

            response_body = {"detail": "Rate limit exceeded"}
            self.send_json_response(429, "Too Many Requests", response_body, headers={"Retry-After": retry_after_str})
            return

        if method == b'CONNECT':
            self.handle_connect(target)
        else:
            self.handle_http_request(target, data)

    def get_request_body(self, data):
        header_end = data.find(b'\r\n\r\n')
        if header_end != -1:
            return data[header_end + 4:].decode('utf-8')
        return ""

    def send_json_response(self, status_code, status_message, body_json, headers=None):
        body_bytes = json.dumps(body_json).encode('utf-8')
        
        response_headers = [
            f"HTTP/1.1 {status_code} {status_message}",
            "Content-Type: application/json",
            f"Content-Length: {len(body_bytes)}",
            "Connection: close",
        ]

        if headers:
            for key, value in headers.items():
                response_headers.append(f"{key}: {value}")

        response_headers.append("")
        response_headers.append("")
        
        response = '\r\n'.join(response_headers).encode('utf-8') + body_bytes
        try:
            self.request.sendall(response)
        except OSError:
            pass # Client might have closed the connection.
        finally:
            self.request.close()

    def handle_control_request(self, method, path, data):
        if method != b'POST':
            self.send_json_response(405, "Method Not Allowed", {"error": "Only POST method is allowed"})
            return

        if path == '/start_rate_limiting':
            body_str = self.get_request_body(data)
            if not body_str:
                self.send_json_response(400, "Bad Request", {"error": "Request body is missing or empty"})
                return
            try:
                body_json = json.loads(body_str)
                test_name = body_json.get('test_name')
                if not test_name or not isinstance(test_name, str):
                    self.send_json_response(400, "Bad Request", {"error": "'test_name' is missing or not a string"})
                    return
            except json.JSONDecodeError:
                self.send_json_response(400, "Bad Request", {"error": "Invalid JSON in request body"})
                return
            
            rate_limiter_state.start_rate_limiting(test_name)
            response_body = {"status": f"rate limiting started for test: {test_name}"}
            self.send_json_response(200, "OK", response_body)

        elif path == '/end_rate_limiting':
            rate_limiter_state.end_rate_limiting()
            response_body = {"status": "rate limiting ended"}
            self.send_json_response(200, "OK", response_body)
        else:
            self.send_json_response(404, "Not Found", {"error": "Endpoint not found"})

    def handle_http_request(self, target, data):
        """Handles HTTP requests like GET, POST, etc."""
        try:
            parsed_url = urlparse(target.decode('utf-8'))
            host = parsed_url.hostname
            port = parsed_url.port
            if port is None:
                port = 443 if parsed_url.scheme == 'https' else 80
        except Exception as e:
            print(f"Could not parse URL for HTTP request: {target}. Error: {e}")
            self.request.close()
            return

        if not host:
            print(f"Invalid host in URL: {target}")
            self.request.close()
            return

        try:
            remote_socket = socket.create_connection((host, port), timeout=10)
            if parsed_url.scheme == 'https':
                context = ssl.create_default_context()
                remote_socket = context.wrap_socket(remote_socket, server_hostname=host)
        except (socket.error, ssl.SSLError) as e:
            print(f"Failed to connect or SSL wrap to {host}:{port}: {e}")
            self.request.close()
            return

        # Modify the request to use a relative path and force connection closing
        # This ensures each request gets its own connection and is logged.
        header_end = data.find(b'\r\n\r\n')
        if header_end == -1:
            # If no header-body separator is found, assume it's a simple request with no body.
            header_end = len(data)

        header_data = data[:header_end]
        body = data[header_end:]

        lines = header_data.split(b'\r\n')
        first_line = lines[0]
        headers = lines[1:]

        method, _, http_version = first_line.split(b' ', 2)

        path = parsed_url.path or '/'
        if parsed_url.query:
            path += '?' + parsed_url.query

        new_first_line = b' '.join([method, path.encode('utf-8'), http_version])

        new_headers = []
        for header in headers:
            # Remove existing connection-related headers, as we're forcing it to close.
            if not header.lower().startswith(b'connection:') and \
               not header.lower().startswith(b'proxy-connection:'):
                new_headers.append(header)
        new_headers.append(b'Connection: close')

        modified_header_part = new_first_line + b'\r\n' + b'\r\n'.join(new_headers)
        modified_request = modified_header_part + body

        try:
            remote_socket.sendall(modified_request)
        except OSError:
            remote_socket.close()
            return

        self.tunnel(self.request, remote_socket)

    def handle_connect(self, target):
        """Handles CONNECT requests for HTTPS traffic."""
        try:
            host, port_str = target.split(b':')
            port = int(port_str)
        except ValueError:
            print(f"Invalid target for CONNECT: {target}")
            self.request.close()
            return

        try:
            remote_socket = socket.create_connection((host.decode('utf-8'), port), timeout=10)
        except socket.error as e:
            print(f"Failed to connect to {host.decode('utf-8')}:{port}: {e}")
            self.request.close()
            return
        
        try:
            self.request.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
        except OSError:
            remote_socket.close()
            return

        self.tunnel(self.request, remote_socket)

    def tunnel(self, client_socket, remote_socket):
        """Tunnels data between the client and the remote server."""
        stop_event = threading.Event()

        def forward(src, dst):
            try:
                while not stop_event.is_set():
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.sendall(data)
            except OSError:
                pass
            finally:
                stop_event.set()

        client_thread = threading.Thread(target=forward, args=(client_socket, remote_socket))
        remote_thread = threading.Thread(target=forward, args=(remote_socket, client_socket))

        client_thread.start()
        remote_thread.start()

        client_thread.join()
        remote_thread.join()

        client_socket.close()
        remote_socket.close()

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

def main():
    HOST, PORT = "localhost", 8004
    
    try:
        server = ThreadingTCPServer((HOST, PORT), ProxyHandler)
        print(f"Starting proxy server on {HOST}:{PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"Could not start proxy server: {e}", file=sys.stderr)
        # The script `run_devrev_snapin_conformance_tests.sh` checks for exit code 69.
        sys.exit(69)

if __name__ == "__main__":
    main()
