import socket  # noqa: F401


def main():
    # server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket = socket.create_server(("0.0.0.0", 4221))
    print("Server is listening on port 4221...")
    
    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")
        request = conn.recv(1024).decode()
        # Extract the requested file path
        request_line = request.split("\n")[0]  # First line of request
        method, path, _ = request_line.split(" ")  # Extract method and path
        print(f"Method: {method}, Path: {path}")
        if(path == "/"):
            response = b"HTTP/1.1 200 OK\r\n\r\n"
        elif(path.startswith("/echo/")):
            string = path.split("/")[2]
            print(f"Echoing: {string}")
            print(string.encode())
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(string.encode())}\r\n\r\n{string}".encode()
        else:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"
            
        conn.sendall(response)
        conn.close()


    


if __name__ == "__main__":
    main()
