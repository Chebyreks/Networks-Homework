import sys, threading
import socket
import json
import time
from game import GameInstance

class P2Pnode:
    def __init__(self, game_instance, self_port, self_host, destination_host, destination_port, start):
        self.game_instance : GameInstance = game_instance
        self.self_port = self_port
        self.self_host = self_host
        self.destination_host = destination_host
        self.destination_port = destination_port
        self.in_connection_socket = None
        self.out_connection_socket = None
        if (start):
            self.start_server()
            self.start_client()
        else:
            self.start_client()
            self.start_server()
        while not self.connection_established():
            time.sleep(1)

    def start_server(self):
        time.sleep(1)
        print(f"Попытка подключиться к порту {self.destination_port}")
        max_attempts = 5
        attempt = 0
        while attempt < max_attempts:
            try:    
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.connect((self.destination_host, self.destination_port))
                self.in_connection_socket = server_socket
                threading.Thread(target=self.receive_messages, daemon=True).start()
                print(f"Подключение к порту {self.destination_port} успешно")
                break
            except Exception as e:
                print(f"Не удалось соединиться с портом {self.destination_port}, повторяю попытку: {str(e)}")
                attempt += 1
                time.sleep(1)

    def receive_messages(self):
        while True:
            data = self.in_connection_socket.recv(1024)
            if not data:
                break
            message = json.loads(data.decode())
            self.game_instance.process_message(message)
        print("Что-то пошло не так (")
        self.end_connections()

    def accept_connections(self, client_socket):
        while True:
            try:
                self.out_connection_socket, addr = client_socket.accept()
                print(f'Подключились к {addr}')
            except Exception as e:
                print(f"Не удалось принять соединение: {str(e)}")

    
    def start_client(self):
        print(f"Попытка принять соединение")
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client_socket.bind((self.self_host, self.self_port))
            client_socket.listen(5)
            print(f'Слушаем порт {self.self_port}')
            threading.Thread(target=self.accept_connections, args=(client_socket,), daemon=True).start()
        except Exception as e:
            print(f"Не удалось прикрепить сокет: {str(e)}")
    
    def connection_established(self):
        return self.in_connection_socket != None and self.out_connection_socket != None
    
    def send_message(self, message):
        try:
            self.out_connection_socket.sendall(json.dumps(message).encode())
        except Exception as e:
            print(f"Всё сломалось, не удалось отправить сообщение: {str(e)}")
            self.end_connections()
    
    def end_connections(self):
        print("Закрываю соединения")
        self.out_connection_socket.close()
        self.out_connection_socket = None
        self.in_connection_socket.close()
        self.in_connection_socket = None