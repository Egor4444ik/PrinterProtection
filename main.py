import time
import threading
from backend.Emulator import PrinterEmulator
from backend.PrintStack import SecurePrintClient

if __name__ == "__main__":
    with open('utils/documents_to_print/test_document.txt', 'w', encoding='utf-8') as f:
        f.write("Конфиденциальный документ для тестирования.\n")
    
    print("=== КЛИЕНТ СИСТЕМЫ ЗАЩИЩЕННОЙ ПЕЧАТИ ===")
    print("Доступные пользователи: user123/password123, employee1/print456, admin/secure789")
    
    client = SecurePrintClient()
    
    while True:
        print("\n" + "="*50)
        print("1 - Отправить документ на печать")
        print("2 - Посмотреть мои задания")
        print("3 - Распечатать документ (эмулятор принтера)")
        print("4 - Выход")
        
        choice = input("Выберите действие: ").strip()
        
        if choice == '1':
            print("Загрузите ваш файл в utils/documents_to_print (по умолчанию там создастся файл test_document.txt)")
            print("Введите название файла вместе с его разрешением: .txt, .docs, ...")
            file_name = input("Название: ")
            print_password = client.submit_print_job('utils/documents_to_print/' + file_name)
            if print_password:
                print(f"➡️ Подойдите к принтеру и введите пароль: {print_password}")
        
        elif choice == '2':
            client.get_user_jobs()
        
        elif choice == '3':
            printer = PrinterEmulator()
            printer.release_job()
        
        elif choice == '4':
            break
        
        else:
            print("❌ Неверный выбор")
    
    print("Работа завершена.")