import os
os.environ['KIVY_NO_CONSOLELOG'] = '1'

import kivy
kivy.require('2.3.0')
import logging


from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from screens import (
    LoginScreen, MainScreen, ProfileScreen,
    SearchScreen, LibraryScreen, AIAssistantScreen,
    MangaDetailScreen
)
from services import Database
from utils.constants import COLORS
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


class MangaApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()  # Единый экземпляр

    def build(self):
        self.title = 'Manga Guide'
        Window.clearcolor = COLORS['light']

        # Автоматический вход тестового пользователя
        try:
            self.db.create_user('test', '1234')
        except:
            pass  # Пользователь уже существует

        success, user_id, username = self.db.verify_user('test', '1234')
        if success:
            self.db.current_user_id = user_id
            self.db.current_username = username
            logging.debug(f"Автоматический вход: {username} (ID: {user_id})")

        # Создание экранов с передачей db
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login', db=self.db))
        sm.add_widget(MainScreen(name='main', db=self.db))
        sm.add_widget(ProfileScreen(name='profile', db=self.db))
        sm.add_widget(SearchScreen(name='search', db=self.db))
        sm.add_widget(LibraryScreen(name='library', db=self.db))
        sm.add_widget(AIAssistantScreen(name='ai', db=self.db))
        sm.add_widget(MangaDetailScreen(name='manga_detail', db=self.db))

        return sm

if __name__ == '__main__':
    MangaApp().run()