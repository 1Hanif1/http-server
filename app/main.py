import socket  # noqa: F401


def main():
    # server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket = socket.create_server(("localhost", 4221))
    response = b"HTTP/1.1 200 OK\r\n\r\n"
    conn, addr = server_socket.accept()
    result = conn.sendall(response)
    if result is None:
        print("Response sent successfully.")
    else:
        print("Failed to send response.")

    


if __name__ == "__main__":
    main()
