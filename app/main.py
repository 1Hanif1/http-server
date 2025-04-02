import socket  # noqa: F401
import threading  # noqa: F401

def build_response(status_code, content_type, body):
    """
    Build an HTTP response.
    :param status_code: HTTP status code
    :param content_type: Content type of the response
    :param body: Body of the response
    :return: Encoded HTTP response
    """
    return f"HTTP/1.1 {status_code} OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(body.encode())}\r\n\r\n{body}".encode()

def handle_request(path, request):
    if path == "/":
        response = b"HTTP/1.1 200 OK\r\n\r\n"
    elif path.startswith("/echo/"):
        string = string = path.split("/")[2] if len(path.split("/")) > 2 else ""
        response = build_response(200, "text/plain", string)
    elif path.startswith("/user-agent"):
        request_line = request.split("\n")[2]  # Third line of request
        user_agent = request_line.split(": ")[1].strip()
        response = build_response(200, "text/plain", user_agent)
    else:
        response = b"HTTP/1.1 404 Not Found\r\n\r\n"
    return response

def handle_client(conn):
    """Handles a single client request"""
    request = conn.recv(1024).decode()
    # Extract the requested file path
    request_line = request.split("\n")[0]  
    
    # First line of request
    method, path, _ = request_line.split(" ")  
    
    # Extract method and path
    if method != "GET":
        response = b"HTTP/1.1 405 Method Not Allowed\r\n\r\n"
    else: 
        # Call the function to handle the request (We assume it is a GET request)
        response = handle_request(path, request)
    conn.sendall(response) # Send the response back to the client
    conn.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.bind(("0.0.0.0", 4221))
    server_socket.listen()  # Listen for incoming connections
    print("Server is listening on port 4221...")
    
    while True:
        conn, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        # Handle the client in a new thread
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.start()

if __name__ == "__main__":
    main()
