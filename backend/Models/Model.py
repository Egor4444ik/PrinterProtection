import sqlite3
import secrets
import hashlib
from datetime import datetime

from typing import Optional, Tuple, List


class SecurePrintDatabase:
    def __init__(self, db_name='backend/Models/secure_print.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица заданий печати
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS print_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    print_password TEXT UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    document_name TEXT NOT NULL,
                    document_data TEXT NOT NULL,
                    page_count INTEGER,
                    status TEXT DEFAULT 'waiting',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    printed_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Добавляем тестовых пользователей если их нет
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                self.add_user('user123', 'password123', 'Иван Иванов')
                self.add_user('employee1', 'print456', 'Петр Петров')
                self.add_user('admin', 'secure789', 'Администратор')
            
            conn.commit()
    
    def add_user(self, username: str, password: str, full_name: str = None) -> bool:
        """Добавление нового пользователя"""
        try:
            password_hash = self.hash_password(password)
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (username, password_hash, full_name) VALUES (?, ?, ?)',
                    (username, password_hash, full_name)
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def verify_user(self, username: str, password: str) -> Tuple[bool, int]:
        """Проверка логина и пароля пользователя"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, password_hash FROM users WHERE username = ?',
                (username,)
            )
            result = cursor.fetchone()
            
            if result and result[1] == self.hash_password(password):
                return True, result[0]
            return False, 0
    
    def add_print_job(self, user_id: int, document_name: str, 
                     document_data: str, page_count: int) -> str:
        """Добавление задания печати в БД"""
        print_password = self.generate_print_password()
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO print_jobs 
                (print_password, user_id, document_name, document_data, page_count) 
                VALUES (?, ?, ?, ?, ?)''',
                (print_password, user_id, document_name, document_data, page_count)
            )
            conn.commit()
        
        return print_password
    
    def get_print_job(self, print_password: str) -> Optional[dict]:
        """Получение задания по паролю"""
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT pj.*, u.username, u.full_name 
                FROM print_jobs pj 
                JOIN users u ON pj.user_id = u.id 
                WHERE pj.print_password = ? AND pj.status = 'waiting'
            ''', (print_password,))
            
            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
    
    def mark_job_printed(self, print_password: str):
        """Пометка задания как распечатанного"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE print_jobs SET status = "printed", printed_at = ? WHERE print_password = ?',
                (datetime.now().isoformat(), print_password)
            )
            conn.commit()
    
    def get_user_jobs(self, user_id: int) -> List[dict]:
        """Получение всех заданий пользователя"""
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM print_jobs 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_old_jobs(self, days: int = 7):
        """Очистка старых заданий"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM print_jobs WHERE created_at < date("now", ?)',
                (f"-{days} days",)
            )
            conn.commit()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def generate_print_password() -> str:
        """Генерация случайного пароля для печати"""
        return ''.join(secrets.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(8))