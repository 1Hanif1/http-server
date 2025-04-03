import socket  # noqa: F401
import threading  # noqa: F401
import os  # noqa: F401
import argparse  # noqa: F401
import zlib

def build_compressed_response(status_code, content_type, encoding_type, body, body_length):
    return f"HTTP/1.1 {status_code} OK\r\nContent-Encoding: {encoding_type}\r\nContent-Type: {content_type}\r\nContent-Length: {body_length}\r\n\r\n{body}".encode()

def build_response(status_code, content_type, body):
    """
    Build an HTTP response.
    :param status_code: HTTP status code
    :param content_type: Content type of the response
    :param body: Body of the response
    :return: Encoded HTTP response
    """
    return f"HTTP/1.1 {status_code} OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(body.encode())}\r\n\r\n{body}".encode()

def get_user_agent(request):
    """
    Extract the User-Agent from the HTTP request.
    :param request: HTTP request string
    :return: User-Agent string
    """
    request_line = request.split("\n")[2]  # Third line of request
    user_agent = request_line.split(": ")[1].strip()
    response = build_response(200, "text/plain", user_agent)
    return response

def get_file_content(file_path):
    """
    Read the content of a file.
    :param file_path: Path to the file
    :return: File content as bytes
    """

    # Check if the file exists
    if os.path.isfile(file_path):  
        try:
            # Open the file in binary mode
            with open(file_path, "rb") as file:  
                content = file.read()

            response = build_response(
                200, "application/octet-stream", content.decode()
            )

        except Exception as e:
            response = b"HTTP/1.1 500 Internal Server Error\r\n\r\n"

    else:
        response = b"HTTP/1.1 404 Not Found\r\n\r\n"
    
    return response

def handle_get_request(path, request, directory="."):
    if path == "/":
        response = b"HTTP/1.1 200 OK\r\n\r\n"
    
    elif path.startswith("/echo/"):
        string = string = path.split("/")[2] if len(path.split("/")) > 2 else ""
        # print(request)  # Print the request for debugging
        request_headers = request.split("\r\n")
        
        accept_encoding = None
        for header in request_headers:
            if header.startswith("Accept-Encoding:"):
                accept_encoding = header.split(": ")[1]
                break
        
        print(f"Accept-Encoding: {accept_encoding}")  # Print the Accept-Encoding header for debugging
        encoders = accept_encoding.split(",") if accept_encoding else []

        # Check if gzip is in the Accept-Encoding header
        for enc in encoders:
            if enc.strip() == "gzip":
                accept_encoding = "gzip"
                break
            else:
                accept_encoding = None

        if accept_encoding == "gzip":
            # If gzip is requested, compress the string
            compressed_string = zlib.compress(string.encode())
            response = build_compressed_response(200, "text/plain", accept_encoding, compressed_string, len(str(compressed_string)))
        else:
            response = build_response(200, "text/plain", string)
    
    elif path.startswith("/user-agent"):
        response = get_user_agent(request)
    
    elif path.startswith("/files/"):
        filename = path.split("/")[2] if len(path.split("/")) > 2 else ""
    
        # Join directory + filename
        file_path = os.path.join(directory, filename)  
        response = get_file_content(file_path)

    else:
        response = b"HTTP/1.1 404 Not Found\r\n\r\n"
    
    return response

def handle_post_request(path, request, directory="."):
    if path == "/":
        response = b"HTTP/1.1 200 OK\r\n\r\n"
    elif path.startswith("/files/"):
        filename = path.split("/")[2] if len(path.split("/")) > 2 else ""
        file_path = os.path.join(directory, filename)  
        
        # Extract the body from the request
        body = request.split("\r\n\r\n")[1]  
        
        # Write the body to the file
        with open(file_path, "wb") as file:  
            file.write(body.encode())
        
        response = b"HTTP/1.1 201 Created\r\n\r\n"
    else:
        response = b"HTTP/1.1 404 Not Found\r\n\r\n"

    return response

def handle_client(conn, directory="."):
    """Handles a single client request"""
    request = conn.recv(1024).decode()
    # print(f"Received request:\n{request}")  # Print the received request
    # Extract the requested file path
    request_line = request.split("\n")[0]  
    
    # First line of request
    method, path, _ = request_line.split(" ")  
    
    # Extract method and path
    if method == "GET":
        response = handle_get_request(path, request, directory)
    elif method == "POST":
        response = handle_post_request(path, request, directory)
    else:
        response = b"HTTP/1.1 405 Method Not Allowed\r\n\r\n" 

    # Send the response back to the client
    conn.sendall(response) 
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Simple HTTP Server")
    parser.add_argument("--directory", required=False, help="Directory to serve files from")
    args = parser.parse_args()  # Parse the command-line arguments
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.bind(("0.0.0.0", 4221))
    server_socket.listen()  # Listen for incoming connections
    print("Server is listening on port 4221...")
    
    while True:
        conn, addr = server_socket.accept()
        # print(f"Accepted connection from {addr}")
        # Handle the client in a new thread
        client_thread = threading.Thread(target=handle_client, args=(conn, args.directory))
        client_thread.start()

if __name__ == "__main__":
    main()
