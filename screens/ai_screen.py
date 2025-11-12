from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

from .base_screen import BackgroundScreen
from services import GeminiAPI, LocalAI
from utils.constants import COLORS


class AIAssistantScreen(BackgroundScreen):
    def __init__(self, db=None, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.clear_widgets()

        self.conversation_history = []

        self.setup_ui()
        self.show_welcome_message()

    def setup_ui(self):
        """Настраивает интерфейс AI помощника"""
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        # Верхняя панель
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))

        back_btn = Button(
            text='Назад',
            background_color=COLORS['primary'],
            size_hint_x=None,
            width=dp(100),
            font_size=dp(16),
            color=[1, 1, 1, 1]
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))

        title_label = Label(
            text='AI Помощник по Манге',
            font_size=dp(20),
            color=COLORS['text_dark'],
            bold=True
        )

        clear_btn = Button(
            text='Очистить',
            size_hint_x=None,
            width=dp(100),
            background_color=COLORS['accent'],
            font_size=dp(14)
        )
        clear_btn.bind(on_press=self.clear_chat)

        top_layout.add_widget(back_btn)
        top_layout.add_widget(title_label)
        top_layout.add_widget(clear_btn)
        layout.add_widget(top_layout)

        # Область чата
        self.chat_scroll = ScrollView()
        self.chat_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(10)
        )
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.chat_scroll.add_widget(self.chat_layout)
        layout.add_widget(self.chat_scroll)

        # Панель ввода
        input_layout = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(10))

        self.user_input = TextInput(
            hint_text='Задайте вопрос о манге...',
            multiline=False,
            font_size=dp(16),
            foreground_color=COLORS['text_dark'],
            background_color=[1, 1, 1, 0.9],
            padding=dp(10)
        )
        self.user_input.bind(on_text_validate=self.send_message)

        send_btn = Button(
            text='Отправить',
            size_hint_x=None,
            width=dp(120),
            background_color=COLORS['secondary'],
            font_size=dp(16)
        )
        send_btn.bind(on_press=self.send_message)

        input_layout.add_widget(self.user_input)
        input_layout.add_widget(send_btn)
        layout.add_widget(input_layout)

        # Индикатор загрузки
        self.loading_label = Label(
            text='',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14),
            color=COLORS['primary']
        )
        layout.add_widget(self.loading_label)

        self.add_widget(layout)

    def show_welcome_message(self):
        """Показывает приветственное сообщение"""
        welcome_text = "Привет! Я AI-помощник по манге.\n\nЯ могу:\n• Ответить на вопросы о манге\n• Порекомендовать мангу по жанрам\n• Помочь найти похожие произведения\n\nЗадайте ваш вопрос ниже!"

        self.add_message("assistant", welcome_text)

    def add_message(self, role, content):
        """Добавляет сообщение в чат"""
        message_card = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            padding=dp(10),
            spacing=dp(10)
        )

        # Аватар
        avatar = Label(
            text='AI' if role == 'assistant' else 'Вы',
            size_hint_x=None,
            width=dp(50),
            font_size=dp(14),
            bold=True,
            color=COLORS['text_dark']
        )

        # Текст сообщения
        message_text = Label(
            text=content,
            size_hint_x=1,
            text_size=(None, None),
            halign='left',
            valign='top',
            color=COLORS['text_dark'],
            font_size=dp(16)
        )
        message_text.bind(texture_size=lambda instance, size: setattr(message_card, 'height', size[1] + dp(20)))

        message_card.add_widget(avatar)
        message_card.add_widget(message_text)
        self.chat_layout.add_widget(message_card)

        # Прокручиваем к низу
        Clock.schedule_once(lambda dt: setattr(self.chat_scroll, 'scroll_y', 0), 0.1)

    def send_message(self, instance):
        """Отправляет сообщение пользователя"""
        user_text = self.user_input.text.strip()
        if not user_text:
            return

        self.user_input.text = ''
        self.add_message("user", user_text)

        self.loading_label.text = "AI думает..."

        Clock.schedule_once(lambda dt: self.get_ai_response(user_text), 0.1)

    def get_ai_response(self, user_question):
        """Получает ответ от AI"""
        try:
            # Сначала пробуем Gemini API
            messages = [
                {"role": "system", "content": "Ты помощник по манге. Отвечай кратко на русском."},
                {"role": "user", "content": user_question}
            ]

            success, response = GeminiAPI.create_chat_completion(messages)

            if success:
                self.handle_ai_response(True, response)
            else:
                # Если API не работает, используем LocalAI
                success, response = LocalAI.create_chat_completion(messages)
                self.handle_ai_response(success, response)

        except Exception as e:
            # В случае ошибки используем LocalAI
            success, response = LocalAI.create_chat_completion([{"role": "user", "content": user_question}])
            self.handle_ai_response(success, response)

    def handle_ai_response(self, success, response):
        """Обрабатывает ответ от AI"""
        self.loading_label.text = ""

        if success:
            self.add_message("assistant", response)
        else:
            error_msg = "Извините, сервис временно недоступен. Попробуйте позже."
            self.add_message("assistant", error_msg)

    def clear_chat(self, instance):
        """Очищает историю чата"""
        self.chat_layout.clear_widgets()
        self.conversation_history = []
        self.show_welcome_message()