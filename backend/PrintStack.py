import json
import socket
import threading
import getpass
from typing import Tuple

from backend.Models.Model import SecurePrintDatabase

class SecurePrintServer:
    def __init__(self, host='localhost', port=9090):
        self.host = host
        self.port = port
        self.db = SecurePrintDatabase()
        self.running = False
    
    def handle_client(self, client_socket, address):
        """Обработка запросов от клиентов"""
        try:
            data = client_socket.recv(4096).decode()
            request = json.loads(data)
            
            if request.get('type') == 'submit_job':
                # Аутентификация и создание задания
                success, user_id = self.db.verify_user(
                    request['user_id'], 
                    request['user_password']
                )
                
                if success:
                    print_password = self.db.add_print_job(
                        user_id,
                        request['metadata']['filename'],
                        request['document_data'],
                        request['metadata']['pages']
                    )
                    response = {'status': 'success', 'print_password': print_password}
                else:
                    response = {'status': 'error', 'message': 'Неверный логин или пароль'}
                
            elif request.get('type') == 'get_job':
                # Получение задания по паролю
                job = self.db.get_print_job(request['password'])
                if job:
                    response = {'status': 'found', 'job': job}
                    self.db.mark_job_printed(request['password'])
                else:
                    response = {'status': 'not_found'}
            
            elif request.get('type') == 'get_user_jobs':
                # Получение заданий пользователя
                success, user_id = self.db.verify_user(
                    request['user_id'], 
                    request['user_password']
                )
                
                if success:
                    jobs = self.db.get_user_jobs(user_id)
                    response = {'status': 'success', 'jobs': jobs}
                else:
                    response = {'status': 'error', 'message': 'Неверный логин или пароль'}
            
            else:
                response = {'status': 'error', 'message': 'Неизвестный тип запроса'}
            
            client_socket.send(json.dumps(response, default=str).encode())
            
        except Exception as e:
            response = {'status': 'error', 'message': str(e)}
            client_socket.send(json.dumps(response).encode())
        finally:
            client_socket.close()
    
    def start_server(self):
        """Запуск сервера"""
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Сервер запущен на {self.host}:{self.port}")
        print(f"База данных: {self.db.db_name}")
        
        while self.running:
            try:
                client_socket, address = server_socket.accept()
                thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address)
                )
                thread.start()
            except:
                break

class SecurePrintClient:
    def __init__(self, server_host='localhost', server_port=9090):
        self.server_host = server_host
        self.server_port = server_port
    
    def get_user_credentials(self) -> Tuple[str, str]:
        """Запрос логина и пароля у пользователя"""
        print("\n=== АУТЕНТИФИКАЦИЯ ===")
        username = input("Логин: ")
        password = getpass.getpass("Пароль: ")
        return username, password
    
    def submit_print_job(self, document_path: str):
        """Отправка задания на печать"""
        try:
            username, password = self.get_user_credentials()
            
            with open(document_path, 'rb') as f:
                document_data = f.read()
            
            metadata = {
                'filename': document_path,
                'pages': len(document_data) // 1000 + 1,
            }
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.server_host, self.server_port))
                request = {
                    'type': 'submit_job',
                    'user_id': username,
                    'user_password': password,
                    'document_data': document_data.decode('latin-1'),
                    'metadata': metadata
                }
                sock.send(json.dumps(request).encode())
                
                response = json.loads(sock.recv(1024).decode())
                
                if response['status'] == 'success':
                    print(f"\n✅ Пароль для печати: {response['print_password']}")
                    return response['print_password']
                else:
                    print(f"❌ Ошибка: {response['message']}")
                    return None
                    
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def get_user_jobs(self):
        """Просмотр своих заданий"""
        try:
            username, password = self.get_user_credentials()
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.server_host, self.server_port))
                request = {
                    'type': 'get_user_jobs',
                    'user_id': username,
                    'user_password': password
                }
                sock.send(json.dumps(request).encode())
                
                response = json.loads(sock.recv(4096).decode())
                
                if response['status'] == 'success':
                    print(f"\n📋 Ваши задания:")
                    for job in response['jobs']:
                        status = "✅ Распечатан" if job['status'] == 'printed' else "⏳ Ожидает"
                        print(f"• {job['document_name']} - {status} - Пароль: {job['print_password']}")
                else:
                    print(f"❌ Ошибка: {response['message']}")
                    
        except Exception as e:
            print(f"❌ Ошибка: {e}")
