
import sqlite3
import hashlib
from config import DB_NAME

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.current_user_id = None
        self.current_username = None
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password_hash TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                manga_id INTEGER,
                title TEXT,
                author TEXT,
                status TEXT DEFAULT 'reading',
                rating INTEGER DEFAULT 0,
                cover_url TEXT,
                notes TEXT,
                progress INTEGER DEFAULT 0,
                total_chapters INTEGER DEFAULT 0,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        self.conn.commit()

    def create_user(self, username, password):
        try:
            cursor = self.conn.cursor()
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                           (username, password_hash))
            self.conn.commit()
            return True, "Регистрация успешна"
        except sqlite3.IntegrityError:
            return False, "Пользователь существует"
        except Exception as e:
            return False, f"Ошибка: {str(e)}"

    def verify_user(self, username, password):
        cursor = self.conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
                       (username, password_hash))
        result = cursor.fetchone()
        if result:
            return True, result[0], result[1]
        return False, None, None

    def add_to_library(self, user_id, manga_id, title, author="", cover_url=""):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id FROM user_library 
                WHERE user_id = ? AND manga_id = ?
            ''', (user_id, manga_id))

            if cursor.fetchone():
                return False, "Манга уже в библиотеке"

            cursor.execute('''
                INSERT INTO user_library (user_id, manga_id, title, author, cover_url) 
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, manga_id, title, author, cover_url))
            self.conn.commit()
            return True, "Манга добавена в библиотеку"
        except Exception as e:
            print(f"Ошибка добавления в библиотеку: {e}")
            return False, f"Ошибка: {str(e)}"

    def get_user_library(self, user_id, status_filter=None):
        try:
            cursor = self.conn.cursor()
            if status_filter:
                cursor.execute('''
                    SELECT id, manga_id, title, author, status, rating, cover_url, notes, progress, total_chapters
                    FROM user_library 
                    WHERE user_id = ? AND status = ?
                    ORDER BY added_date DESC
                ''', (user_id, status_filter))
            else:
                cursor.execute('''
                    SELECT id, manga_id, title, author, status, rating, cover_url, notes, progress, total_chapters
                    FROM user_library 
                    WHERE user_id = ? 
                    ORDER BY added_date DESC
                ''', (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения библиотеки: {e}")
            return []

    def get_library_stats(self, user_id):
        """Получает статистику библиотеки"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM user_library 
                WHERE user_id = ? 
                GROUP BY status
            ''', (user_id,))
            stats = cursor.fetchall()

            stats_dict = {}
            total = 0
            for status, count in stats:
                if status:
                    stats_dict[status] = count
                    total += count

            stats_dict['total'] = total
            return stats_dict
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return {}

    def update_manga_status(self, library_id, new_status):
        """Обновляет статус манги в библиотеке"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE user_library 
                SET status = ? 
                WHERE id = ?
            ''', (new_status, library_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка обновления статуса: {e}")
            return False

    def update_manga_progress(self, library_id, progress, total_chapters=None):
        """Обновляет прогресс чтения"""
        try:
            cursor = self.conn.cursor()
            if total_chapters:
                cursor.execute('''
                    UPDATE user_library 
                    SET progress = ?, total_chapters = ?
                    WHERE id = ?
                ''', (progress, total_chapters, library_id))
            else:
                cursor.execute('''
                    UPDATE user_library 
                    SET progress = ?
                    WHERE id = ?
                ''', (progress, library_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка обновления прогресса: {e}")
            return False

    def remove_from_library(self, library_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM user_library WHERE id = ?', (library_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка удаления из библиотеки: {e}")
            return False

    def is_in_library(self, user_id, manga_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id FROM user_library 
                WHERE user_id = ? AND manga_id = ?
            ''', (user_id, manga_id))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Ошибка проверки библиотеки: {e}")
            return False