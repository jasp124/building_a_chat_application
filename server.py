import socket
import threading
import ssl
import bcrypt

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {} #username: socket
        self.user_credentials = {
            "alice": "Passwords123",
            "bob": "sercurepass",
            "charlie": "letmein"
        }
    
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host} : {self.port}")

        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"New connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket))
            client_handler.start()
    
    def handle_client(self, client_socket):
        #wrap the socket with ssl/tts
        sercure_socket = ssl.wrap_socket(client_socket, server_side=True, certfile="server.crt", keyfile="server.key")

        #authentication
        username = self.authenticate_client(sercure_socket)
        if not username:
            sercure_socket.close()
            return
        
        self.clients[username] = sercure_socket
        self.broadcast_message(f'SYSTEM|Server|ALL|{username} has joined the chat')

        while True:
            try:
                message = sercure_socket.recv(1024).decode('utf-8')
                if message:
                    self.process_message(username, message)
                else:
                    break
            except Exception as e:
                print(f"Error handling client {username}: {e}")
                break
        self.remove_client(username)
        sercure_socket.close()
    
    def authenticate_client(self, client_socket):
        client_socket.send("Please enter your username:".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8').strip()
        client_socket.send("Please enter your password:".encode('utf-8'))
        password = client_socket.recv(1024).decode('utf-8').strip()

        if username in self.user_credentials and self.user_credentials[username] == password:
            client_socket.send('Authentication successful'.encode('utf-8'))
            return username
        else:
            client_socket.send('Authentication failed'.encode('utf-8'))
            return None
        
    def process_message(self, sender, message):
        msg_type, recipient, content = message.split('|', 2)
        if msg_type == 'PUBLIC':
            self.broadcast_message(f'PUBLIC{sender}|ALL|{content}')
        elif msg_type == "PRIVATE":
            self.send_private_message(sender, recipient, content)
    
    def broadcast_message(self, message):
        for client_socket in self.clients.values():
            try:
                client_socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting message: {e}")
    
    def send_private_message(self, sender, recipient, content):
        if recipient in self.clients:
            try:
                self.clients[recipient].send(f"PRIVATE|{sender}|{recipient}|{content}".encode('utf-8'))
            except Exception as e:
                print(f"Error sending private message: {e}")
        else:
            self.clients(sender).send(f"SYSTEM|Server|[{sender}|User {recipient}| is not online]".encode('utf-8'))

    def remove_clients(self, username):
        if username in self.clients:
            del self.clients[username]
            self.broadcast_message(f"SYSTEM|Server|ALL|[{username}|has left the chat.")



class UserManager:
    def __init__(self):
        self.users = {}#username: hashed_password

    def creat_user(self, username, password):
        if username in self.users:
            return False
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.users[username] = hashed_password
        return True
    
    def authenticate_user(self, username, password):
        if username not in self.users:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.users[username])

if __name__ == "__main__":
    server = ChatServer('localhost', 12345)
    server.start()