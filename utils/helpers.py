
from kivy.metrics import dp

def validate_email(email):
    """Проверяет валидность email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_number(number):
    """Форматирует числа для отображения"""
    if number >= 1000000:
        return f"{number/1000000:.1f}M"
    elif number >= 1000:
        return f"{number/1000:.1f}K"
    return str(number)

def calculate_read_percentage(progress, total):
    """Рассчитывает процент прочитанного"""
    if total and total > 0:
        return min(100, int((progress / total) * 100))
    return 0