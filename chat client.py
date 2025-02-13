import socket
import threading
import ssl

class ChatClient():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
    
    def connect(self):
        # Wrap the socket with SSL/TLS
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        self.socket = context.wrap_socket(self.socket, server_hostname=self.host)

        self.socket.connect((self.host, self.port))
        self.authenticate()

        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        self.send_messages()

    def authenticate(self):
        username_prompt = self.socket.recv(1024).decode('utf-8')
        print(username_prompt)
        self.username = input()
        self.socket.send(self.username.encode('utf-8'))

        password_prompt = self.socket.recv(1024).decode('utf-8')
        print(password_prompt)
        password = input()
        self.socket.send(password.encode('utf-8'))

        response = self.socket.recv(1024).decode('utf-8')
        print(response)
        if "failed" in response.lower():
            print("Authentication failed. Exiting.")
            self.socket.close()
            exit()

        def receive_messages(self):
            while True:
                try:
                    message = self.socket.recv(1024).decode('utf-8')
                    msg_type, sender, recipient, content = message.split('|', 3)
                    if msg_type == "PUBLIC":
                        print(f"{sender}: {content}")
                    elif msg_type == "PRIVATE":
                        print(f"[Private] {sender}: {content}")
                    elif msg_type == "SYSTEM":
                        print(f"[System] {content}")
                except Exception as e:
                    print(f"Error receiving message: {e}")
                    break

        def send_messages(self):
            while True:
                message = input()
                if message.lower() == 'quit':
                    break
                elif message.startswith('@'):
                    recipient, content = message[1:].split(' ', 1)
                    self.socket.send(f"PRIVATE|{recipient}|{content}".encode('utf-8'))
                else:
                    self.socket.send(f"PUBLIC|ALL|{message}".encode('utf-8'))

            self.socket.close()

if __name__ == "__main__":
    client = ChatClient('localhost', 12345)
    client.connect()
