
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

from .base_screen import BackgroundScreen
from services import Database
from utils.constants import COLORS
import logging

class LoginScreen(BackgroundScreen):
    def __init__(self, db=None, **kwargs):  # Единственный __init__
        super().__init__(**kwargs)
        self.db = db  # Сохраняем переданную базу данных
        self.clear_widgets()
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс входа"""
        content_layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))

        # Карточка для формы входа
        form_card = BoxLayout(
            orientation='vertical',
            padding=dp(25),
            spacing=dp(20),
            size_hint=(0.85, 0.7),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Добавляем фон карточке
        with form_card.canvas.before:
            Color(*COLORS['light'])
            RoundedRectangle(pos=form_card.pos, size=form_card.size, radius=[dp(15)])

        # Заголовок
        title = Label(
            text='Manga Guide',
            font_size=dp(32),
            color=COLORS['text_dark'],
            bold=True
        )
        form_card.add_widget(title)

        subtitle = Label(
            text='Вход в систему',
            font_size=dp(20),
            color=COLORS['text_dark']
        )
        form_card.add_widget(subtitle)

        # Поля ввода
        self.username = TextInput(
            hint_text='Введите логин',
            size_hint_y=None,
            height=dp(60),
            font_size=dp(18),
            multiline=False,
            foreground_color=COLORS['text_dark'],
            background_color=[1, 1, 1, 0.9],
            padding=dp(15)
        )
        form_card.add_widget(self.username)

        self.password = TextInput(
            hint_text='Введите пароль',
            password=True,
            size_hint_y=None,
            height=dp(60),
            font_size=dp(18),
            multiline=False,
            foreground_color=COLORS['text_dark'],
            background_color=[1, 1, 1, 0.9],
            padding=dp(15)
        )
        form_card.add_widget(self.password)

        # Кнопки
        btn_layout = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(15))

        login_btn = Button(
            text='Войти',
            background_color=COLORS['primary'],
            font_size=dp(18),
            color=[1, 1, 1, 1]
        )
        login_btn.bind(on_press=self.try_login)

        reg_btn = Button(
            text='Регистрация',
            background_color=COLORS['secondary'],
            font_size=dp(18),
            color=[1, 1, 1, 1]
        )
        reg_btn.bind(on_press=self.show_register)

        btn_layout.add_widget(login_btn)
        btn_layout.add_widget(reg_btn)
        form_card.add_widget(btn_layout)

        # Сообщение
        self.message = Label(
            text='',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16),
            color=[1, 0, 0, 1]
        )
        form_card.add_widget(self.message)

        content_layout.add_widget(form_card)
        self.add_widget(content_layout)

    def try_login(self, instance):
        try:
            user = self.username.text.strip()
            pwd = self.password.text.strip()

            if not user or not pwd:
                self.show_message("Заполните все поля")
                return

            # ИСПРАВЛЕНО: db на self.db
            success, user_id, username = self.db.verify_user(user, pwd)

            if success:
                self.db.current_user_id = user_id
                self.db.current_username = username
                logging.debug(f"Успешный вход! User ID: {user_id}, Username: {username}")
                self.show_message("Успешный вход!", [0, 0.5, 0, 1])
                Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'main'), 1)
            else:
                self.show_message("Неверный логин или пароль")
        except Exception as e:
            self.show_message(f"Ошибка: {str(e)}")

    def show_register(self, instance):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

            # Фон для попапа
            with content.canvas.before:
                Color(*COLORS['light'])
                RoundedRectangle(pos=content.pos, size=content.size, radius=[dp(10)])

            content.add_widget(Label(text='Регистрация', font_size=dp(24), color=COLORS['text_dark']))

            user_input = TextInput(
                hint_text='Логин (мин. 3 символа)',
                size_hint_y=None,
                height=dp(60),
                font_size=dp(18),
                foreground_color=COLORS['text_dark'],
                background_color=[1, 1, 1, 0.9]
            )
            pwd_input = TextInput(
                hint_text='Пароль (мин. 4 символа)',
                password=True,
                size_hint_y=None,
                height=dp(60),
                font_size=dp(18),
                foreground_color=COLORS['text_dark'],
                background_color=[1, 1, 1, 0.9]
            )
            confirm_input = TextInput(
                hint_text='Подтвердите пароль',
                password=True,
                size_hint_y=None,
                height=dp(60),
                font_size=dp(18),
                foreground_color=COLORS['text_dark'],
                background_color=[1, 1, 1, 0.9]
            )

            content.add_widget(user_input)
            content.add_widget(pwd_input)
            content.add_widget(confirm_input)

            msg_label = Label(text='', size_hint_y=None, height=dp(40), font_size=dp(16), color=COLORS['text_dark'])
            content.add_widget(msg_label)

            btn_layout = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(10))

            def register(btn):
                try:
                    user = user_input.text.strip()
                    pwd = pwd_input.text.strip()
                    confirm = confirm_input.text.strip()

                    if len(user) < 3:
                        msg_label.text = "Логин слишком короткий (мин. 3 символа)"
                        return

                    if len(pwd) < 4:
                        msg_label.text = "Пароль слишком короткий (мин. 4 символа)"
                        return

                    if pwd != confirm:
                        msg_label.text = "Пароли не совпадают"
                        return

                    # ИСПРАВЛЕНО: db на self.db
                    success, message = self.db.create_user(user, pwd)
                    msg_label.text = message
                    if success:
                        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)
                        self.username.text = user
                        self.password.text = pwd
                except Exception as e:
                    msg_label.text = f"Ошибка: {str(e)}"

            def cancel(btn):
                popup.dismiss()

            reg_btn = Button(
                text='Зарегистрироваться',
                background_color=COLORS['secondary'],
                font_size=dp(18),
                color=[1, 1, 1, 1]
            )
            reg_btn.bind(on_press=register)

            cancel_btn = Button(
                text='Отмена',
                background_color=COLORS['accent'],
                font_size=dp(18),
                color=[1, 1, 1, 1]
            )
            cancel_btn.bind(on_press=cancel)

            btn_layout.add_widget(reg_btn)
            btn_layout.add_widget(cancel_btn)
            content.add_widget(btn_layout)

            popup = Popup(
                title='',
                content=content,
                size_hint=(0.9, 0.8),
                background='',
                separator_color=[0, 0, 0, 0]
            )
            popup.open()
        except Exception as e:
            self.show_message(f"Ошибка открытия окна: {str(e)}")

    def show_message(self, text, color=None):
        try:
            self.message.text = text
            if color:
                self.message.color = color
            else:
                self.message.color = [1, 0, 0, 1]
            Clock.schedule_once(lambda dt: setattr(self.message, 'text', ''), 3)
        except Exception as e:
            print(f"ERROR: {str(e)}")
