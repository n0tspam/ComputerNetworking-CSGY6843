# import socket module
from socket import *
import sys  # In order to terminate the program


def webServer(port=13331):
    serverSocket = socket(AF_INET, SOCK_STREAM)

    serverSocket.bind(('127.0.0.1', port))
    serverSocket.listen(1)
    while True:
        # Establish the connection

        connectionSocket, addr = serverSocket.accept()
        try:
            message = connectionSocket.recv(1024)
            filename = message.split()[1]
            f = open(filename[1:])
            outputdata = f.read()

            # Send one HTTP header line into socket
            # Fill in start
            connectionSocket.send('HTTP/1.1 200 OK\r\n'.encode())
            # Fill in end
            # Send the content of the requested file to the client
            connectionSocket.sendall(bytes(outputdata, "UTF-8"))
            print(outputdata)
            connectionSocket.send("\r\n".encode())
            connectionSocket.close()
        except IOError as e:
            # Send response message for file not found (404)
            # Fill in start

            # connectionSocket.send(
            #     bytes("HTTP/1.1 404 Not Found\r\n\r\n", "UTF-8"))
            connectionSocket.send(bytes(
                "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n", "UTF-8"))
            # Fill in end
            # Close client socket
            # Fill in start
            connectionSocket.close()
            # Fill in end

    serverSocket.close()
    sys.exit()  # Terminate the program after sending the corresponding data


if __name__ == "__main__":
    webServer(13331)
