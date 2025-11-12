
import os
import random
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage, Image
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from utils.constants import ANIME_BACKGROUNDS, COLORS


class BackgroundScreen(Screen):
    """Базовый класс для всех экранов с фоном"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_added = False

    def on_pre_enter(self):
        if not self.background_added:
            self.add_background()
            self.background_added = True

    def add_background(self):
        """Добавляет аниме фон на экран"""
        # Создаем layout для фона и контента
        main_layout = BoxLayout(orientation='vertical')

        # Проверяем доступные фоны
        available_backgrounds = []
        for bg in ANIME_BACKGROUNDS:
            if os.path.exists(bg):
                available_backgrounds.append(bg)

        if not available_backgrounds:
            # Если нет локальных файлов, используем черный фон
            with main_layout.canvas.before:
                Color(0.1, 0.1, 0.1, 1)
                Rectangle(pos=main_layout.pos, size=main_layout.size)
        else:
            # Аниме фон
            background = Image(
                source=random.choice(available_backgrounds),
                allow_stretch=True,
                keep_ratio=False,
                opacity=0.7
            )

            # Overlay для затемнения фона
            with background.canvas.before:
                Color(0, 0, 0, 0.3)
                self.overlay = Rectangle(pos=background.pos, size=background.size)

            background.bind(pos=self.update_overlay, size=self.update_overlay)
            main_layout.add_widget(background)

        # Контейнер для контента поверх фона
        content_layout = BoxLayout(orientation='vertical')

        # Переносим существующие виджеты в новый layout
        for child in self.children[:]:
            self.remove_widget(child)
            content_layout.add_widget(child)

        main_layout.add_widget(content_layout)
        self.add_widget(main_layout)

    def update_overlay(self, instance, value):
        """Обновляет позицию оверлея"""
        if hasattr(self, 'overlay'):
            self.overlay.pos = instance.pos
            self.overlay.size = instance.size