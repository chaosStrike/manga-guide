# screens/profile_screen.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp

from .base_screen import BackgroundScreen
from services import Database
from utils.constants import COLORS, READING_STATUSES


class ProfileScreen(BackgroundScreen):
    def __init__(self, db=None, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.clear_widgets()
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс профиля"""
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))

        back_btn = Button(
            text='⬅ Назад',
            background_color=COLORS['primary'],
            size_hint_y=None,
            height=dp(60),
            font_size=dp(18),
            color=[1, 1, 1, 1]
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)

        self.info = Label(
            text='',
            font_size=dp(16),
            color=COLORS['text_dark'],
            halign='left',
            valign='top'
        )
        layout.add_widget(self.info)

        self.add_widget(layout)

    def on_pre_enter(self):
        try:
            user_id = self.db.current_user_id or "—"
            username = self.db.current_username or "—"

            # Получаем расширенную статистику
            stats = self.db.get_library_stats(user_id)

            stats_text = f"ID: {user_id}\nЛогин: {username}\n\n"
            stats_text += " Статистика библиотеки:\n"
            stats_text += f"• Всего манг: {stats.get('total', 0)}\n"

            for status_key, status_text in READING_STATUSES.items():
                count = stats.get(status_key, 0)
                if count > 0:
                    icon = status_text.split(' ')[0]
                    stats_text += f"• {icon} {status_text.split(' ')[1]}: {count}\n"

            self.info.text = stats_text
        except Exception as e:
            self.info.text = f"Ошибка загрузки: {str(e)}"
