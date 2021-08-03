import socket  # To manage sockets
import select  # To manage many connections on any system

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 4444

addressfamily = socket.AF_INET  # IPv4
connection = socket.SOCK_STREAM  # TCP

# Socket created SERVER
server_socket = socket.socket(addressfamily, connection)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()

# List of sockets that will be used
sockets_list = [server_socket]

# socket => user header and name as data
clients = {}

print(f'Connection from {IP}:{PORT}')

# Handles message receiving
def receive_message(client_socket):

    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())
        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False


# For listen connections
while True:

    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accepts and returns socket used by client and the ip/port
            client_socket, client_address = server_socket.accept()

            # Client should send his name right away, receive it
            username = receive_message(client_socket)

            # If False - client disconnected before he sent his name
            if username is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save username and username header
            clients[client_socket] = username

            print('Connection accepted from {}:{}, Username: {}'.format(
                *client_address, username['data'].decode('utf-8')))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)
            if message is False:
                print('Closed connection from: {}'.format(
                    clients[notified_socket]['data'].decode('utf-8')))

                sockets_list.remove(notified_socket)
                del clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            username = clients[notified_socket]

            print('Received message from {}: {}'.format(
                username["data"].decode("utf-8"), message["data"].decode("utf-8")))

            # Iterate over connected clients and broadcast message
            for client_socket in clients:

                # Send message to other clients
                if client_socket != notified_socket:

                    # Send username and message with respective headers
                    client_socket.send(
                        username['header'] + username['data'] + message['header'] + message['data'])

    # Handle socket exceptions if necessary
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
