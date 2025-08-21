import json
import socket
import time

class PrinterEmulator:
    def __init__(self, server_host='localhost', server_port=9090):
        self.server_host = server_host
        self.server_port = server_port
    
    def release_job(self):
        """Процесс печати на принтере"""
        try:
            print("\n=== ПАНЕЛЬ ПРИНТЕРА ===")
            print_password = input("Введите пароль для печати: ").strip().upper()
            
            print(f"🔄 Подключаюсь к серверу {self.server_host}:{self.server_port}...")
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            try:
                sock.connect((self.server_host, self.server_port))
                print("✅ Подключение к серверу установлено")
                
                request = {
                    'type': 'get_job',
                    'password': print_password
                }
                
                print("📨 Отправляю запрос серверу...")
                sock.send(json.dumps(request).encode())
                
                print("⏳ Ожидаю ответ от сервера...")
                response_data = sock.recv(4096).decode()
                print(f"📨 Получен ответ: {response_data}")
                
                response = json.loads(response_data)
                
                if response['status'] == 'found':
                    job = response['job']
                    print(f"\n🖨️  Печатаем: {job['document_name']}")
                    print(f"👤 Пользователь: {job['full_name']}")
                    print(f"📊 Страниц: {job['page_count']}")
                    print("✅ Документ распечатан!")
                    return True
                else:
                    print("❌ Неверный пароль или документ уже распечатан")
                    return False
                    
            except socket.timeout:
                print("❌ Таймаут подключения к серверу")
                return False
            except ConnectionRefusedError:
                print("❌ Сервер недоступен. Запущен ли сервер?")
                return False
            finally:
                sock.close()
                    
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка декодирования JSON: {e}")
            return False
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return False