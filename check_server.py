import socket

def check_server(host='localhost', port=9090):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((host, port))
        sock.close()
        print("✅ Сервер запущен и доступен")
        return True
    except:
        print("❌ Сервер недоступен")
        return False

if __name__ == "__main__":
    check_server()