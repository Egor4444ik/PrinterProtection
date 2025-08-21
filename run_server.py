from backend.PrintStack import SecurePrintServer

if __name__ == "__main__":
    print("Запуск сервера защищенной печати...")
    server = SecurePrintServer()
    server.start_server()