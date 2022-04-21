# 1077466 - Marvin Minuth
import socket
import sys
import threading


def server():
    s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_sock.bind(('127.0.0.1', 123))
    s_sock.listen()

    # User und Namen speichern
    users = []
    usernames = []

    # Nachricht an alle User außer Absender*in verschicken
    def broadcast(message, sender):
        for user in users:
            if user == sender:
                continue
            user.send(message.encode('utf-8'))

    # Nachricht erhalten, verarbeiten und verschicken
    def handle(user, username):
        while True:
                message = user.recv(255)
                # Erstes Byte gibt Laenge der Nachricht an:
                length = message[0]
                # restlichen Bytes sind Nachricht:
                message = message[1:length + 1]
                # Name wird der Nachricht hinzugefügt und Nachricht ggf. gekürzt
                message = f"{username}: {message.decode('utf-8')}"
                if len(message) > 255:
                    message = message[:255]
                print(f"Nachricht der Laenge {length} von {message}")
                # Nachricht verbreiten
                broadcast(message, user)

    while True:
        # Registrierung eines Users, erste Nachricht ist Username
        c_sock, c_addr = s_sock.accept()
        users.append(c_sock)
        username = c_sock.recv(255).decode()
        usernames.append(username)
        print(f'{username} registered.')
        c_sock.send("Connected to server.".encode('utf-8'))
        t = threading.Thread(target=handle, args=(c_sock, username))
        t.start()


def client(username):
    # User registriert sich, sendet Username als erste Nachricht
    c_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c_sock.connect(('127.0.0.1', 123))
    c_sock.send(username.encode())

    def receive():
        while True:
            message = c_sock.recv(255).decode('utf-8')
            print(message)

    def write():
        while True:
            message = f'{input("")}'
            length = len(message)
            if length > 255:
                print("Nachricht zu lang.")
            # wandle Int "Laenge" in Byte um
            length_byte = length.to_bytes(1, 'big')
            # wandle String in Byte um
            message = message.encode('utf-8')
            # Bytes zusammenführen und an Server schicken
            data_to_send = length_byte + message
            c_sock.send(data_to_send)

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()


def main():
    if len(sys.argv) != 2:
        print("Usage: \"{0} -l\" for server or \"{0} -c\" for clients".format(sys.argv[0]))
        sys.exit()
    if sys.argv[1].lower() == '-l':
        server()
    if sys.argv[1].lower() == '-c':
        name = input("Enter your name: ")
        client(name)
    else:
        print("Usage: \"{0} -l\" or \"-c\"".format(sys.argv[0]))
        sys.exit()


if __name__ == '__main__':
    main()
