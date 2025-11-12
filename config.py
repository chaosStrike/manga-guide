# config.py
import os

# Настройки приложения
APP_NAME = "Manga Guide"
APP_VERSION = "1.0"

# Настройки API
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-5a770a0168794b5d8f11f4d4ccf99b76")

# Настройки базы данных
DB_NAME = "manga.db"

# Настройки UI
WINDOW_SIZE = (400, 700)