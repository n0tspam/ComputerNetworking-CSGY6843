from socket import *


def smtp_client(port=1025, mailserver='127.0.0.1'):
    msg = "\r\n My message"

    mailserver = (mailserver, port)  # Fill in start #Fill in end
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(mailserver)

    recv = clientSocket.recv(1024).decode()
    if recv[:3] != '220':
        print('220 reply not received from server.')

    # Send HELO command and print server response.
    heloCommand = 'HELO Alice\r\n'
    clientSocket.send(heloCommand.encode())
    recv1 = clientSocket.recv(1024).decode()
    print("Message after EHLO command:" + recv1)
    print(recv1)
    if recv1[:3] != '250':
        print('250 reply not received from server.')

   # Send MAIL FROM command and print server response.
    mailFrom = "MAIL FROM:<wg2159@nyu.edu>\r\n"
    clientSocket.send(mailFrom.encode())
    recv2 = clientSocket.recv(1024).decode()

   # Send RCPT TO command and print server response.
    rcptTo = "RCPT TO:<wg2159@nyu.edu>\r\n"
    clientSocket.send(rcptTo.encode())
    recv3 = clientSocket.recv(1024).decode()

   # Send DATA command and print server response.
    data = "DATA\r\n"
    clientSocket.send(data.encode())
    recv4 = clientSocket.recv(1024).decode()

   # Send message data.
    clientSocket.send(msg.encode())

   # Message ends with a single period.
    clientSocket.send("\r\n.\r\n".encode())
    recv_msg = clientSocket.recv(1024).decode()

   # Send QUIT command and get server response.
    quit = "QUIT\r\n"
    clientSocket.send(quit.encode())
    recv5 = clientSocket.recv(1024).decode()
    clientSocket.close()


if __name__ == '__main__':
    smtp_client(1025, '127.0.0.1')
