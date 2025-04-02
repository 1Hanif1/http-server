import socket  # noqa: F401

def build_response(status_code, content_type, body):
    """
    Build an HTTP response.
    :param status_code: HTTP status code
    :param content_type: Content type of the response
    :param body: Body of the response
    :return: Encoded HTTP response
    """
    return f"HTTP/1.1 {status_code} OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(body.encode())}\r\n\r\n{body}".encode()

def main():
    # server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket = socket.create_server(("0.0.0.0", 4221))
    print("Server is listening on port 4221...")
    
    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")
        request = conn.recv(1024).decode()
        print(f"{request}")
        # Extract the requested file path
        request_line = request.split("\n")[0]  # First line of request
        method, path, _ = request_line.split(" ")  # Extract method and path
        print(f"Method: {method}, Path: {path}")
        if path == "/":
            response = b"HTTP/1.1 200 OK\r\n\r\n"
        elif path.startswith("/echo/"):
            string = path.split("/")[2]
            response = build_response(200, "text/plain", string)
        elif path.startswith("/user-agent"):
            request_line = request.split("\n")[2]  # Third line of request
            user_agent = request_line.split(": ")[1].strip()
            response = build_response(200, "text/plain", user_agent)
        else:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"
            
        conn.sendall(response)
        conn.close()


    


if __name__ == "__main__":
    main()
