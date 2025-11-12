from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

from .base_screen import BackgroundScreen
from services import Database
from utils.constants import COLORS

class MainScreen(BackgroundScreen):
    def __init__(self, db=None, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.clear_widgets()
        self.setup_ui()

    def setup_ui(self):
        """Настраивает главное меню"""
        content_layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))

        # Карточка меню
        menu_card = BoxLayout(
            orientation='vertical',
            padding=dp(25),
            spacing=dp(20),
            size_hint=(0.9, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Фон карточки
        with menu_card.canvas.before:
            Color(*COLORS['light'])
            RoundedRectangle(pos=menu_card.pos, size=menu_card.size, radius=[dp(20)])

        self.welcome = Label(
            text='Главное меню',
            font_size=dp(28),
            color=COLORS['text_dark']
        )
        menu_card.add_widget(self.welcome)

        buttons = [
            ('Профиль', 'profile', COLORS['primary']),
            ('Поиск манги', 'search', COLORS['secondary']),
            ('Моя библиотека', 'library', COLORS['primary']),
            ('AI Помощник', 'ai', COLORS['secondary']),
            ('Выйти', 'logout', COLORS['accent']),
        ]

        for text, screen, color in buttons:
            btn = Button(
                text=text,
                background_color=color,
                size_hint_y=None,
                height=dp(70),
                font_size=dp(18),
                color=[1, 1, 1, 1]
            )

            if screen == 'logout':
                btn.bind(on_press=self.logout)
            else:
                def create_callback(s):
                    return lambda x: setattr(self.manager, 'current', s)
                btn.bind(on_press=create_callback(screen))

            menu_card.add_widget(btn)

        content_layout.add_widget(menu_card)
        self.add_widget(content_layout)

    def on_pre_enter(self):
        try:
            user = self.db.current_username or "Гость"
            self.welcome.text = f"Привет, {user}!"
        except Exception as e:
            print(f"ERROR: {str(e)}")

    def logout(self, instance):
        try:
            self.db.current_user_id = None
            self.db.current_username = None
            self.manager.current = 'login'
        except Exception as e:
            print(f"ERROR: {str(e)}")
