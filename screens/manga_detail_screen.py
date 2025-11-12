# screens/manga_detail_screen.py
import webbrowser
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

from .base_screen import BackgroundScreen
from services import MangaAPI, Database
from utils.constants import COLORS
import logging


class MangaDetailScreen(BackgroundScreen):
    def __init__(self, db=None, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.clear_widgets()

        self.current_manga_id = None
        self.current_manga_data = None

        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс детальной информации"""
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Верхняя панель
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))

        self.back_btn = Button(
            text='⬅ Назад',
            background_color=COLORS['primary'],
            size_hint_x=None,
            width=dp(100),
            font_size=dp(16),
            color=[1, 1, 1, 1]
        )
        self.back_btn.bind(on_press=self.go_back)

        self.title_label = Label(
            text='Детали манги',
            font_size=dp(18),
            color=COLORS['text_dark'],
            halign='left'
        )

        top_layout.add_widget(self.back_btn)
        top_layout.add_widget(self.title_label)
        top_layout.add_widget(Label())  # Пустой виджет для выравнивания

        layout.add_widget(top_layout)

        # Основной контент
        self.scroll = ScrollView()
        self.content_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))

        self.scroll.add_widget(self.content_layout)
        layout.add_widget(self.scroll)

        self.add_widget(layout)

    def load_manga(self, manga_id):
        """Загружает данные манги и отображает их"""
        logging.debug(f"Загружаем мангу с ID: {manga_id}")
        self.current_manga_id = manga_id
        self.content_layout.clear_widgets()

        # Показываем индикатор загрузки
        loading_label = Label(
            text='Загрузка...',
            font_size=dp(18),
            color=COLORS['text_dark'],
            size_hint_y=None,
            height=dp(100)
        )
        self.content_layout.add_widget(loading_label)

        def load_thread(dt):
            try:
                print(f"DEBUG: Запрашиваем данные манги {manga_id}...")
                manga_data = MangaAPI.get_manga_by_id(manga_id)
                print(f"DEBUG: Получены данные: {manga_data is not None}")
                if manga_data:
                    print(f"DEBUG: Название: {manga_data['title']}")
                Clock.schedule_once(lambda dt: self.display_manga(manga_data), 0)
            except Exception as e:
                print(f"DEBUG: Ошибка загрузки: {e}")
                Clock.schedule_once(lambda dt: self.show_error(str(e)), 0)

        Clock.schedule_once(load_thread, 0.1)

    def display_manga(self, manga_data):
        """Отображает данные манги"""
        if not manga_data:
            self.show_error("Не удалось загрузить данные манги")
            return

        self.current_manga_data = manga_data
        self.content_layout.clear_widgets()

        # Обложка и основная информация
        cover_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(200), spacing=dp(15))

        # Обложка
        cover_url = None
        if manga_data.get('coverImage'):
            cover_url = (manga_data['coverImage'].get('extraLarge') or
                         manga_data['coverImage'].get('large') or
                         manga_data['coverImage'].get('medium'))

        if cover_url:
            cover = AsyncImage(
                source=cover_url,
                size_hint_x=None,
                width=dp(150),
                nocache=True
            )
            cover_layout.add_widget(cover)
        else:
            no_cover = Label(
                text='Нет обложки',
                font_size=dp(14),
                color=COLORS['text_dark'],
                size_hint_x=None,
                width=dp(150)
            )
            cover_layout.add_widget(no_cover)

        # Основная информация
        info_layout = BoxLayout(orientation='vertical', spacing=dp(5))

        title = manga_data['title']['romaji'] or manga_data['title']['english'] or 'Без названия'
        title_label = Label(
            text=title,
            font_size=dp(20),
            color=COLORS['text_dark'],
            halign='left',
            text_size=(Window.width - dp(180), None)
        )
        info_layout.add_widget(title_label)

        # Статус
        if manga_data.get('status'):
            status_ru = {
                'FINISHED': ' Завершена',
                'RELEASING': ' Выходит',
                'NOT_YET_RELEASED': ' Не вышла',
                'CANCELLED': ' Отменена',
                'HIATUS': ' Заморожена'
            }
            status = status_ru.get(manga_data['status'], manga_data['status'])
            status_label = Label(
                text=f"Статус: {status}",
                font_size=dp(16),
                color=COLORS['text_dark'],
                halign='left'
            )
            info_layout.add_widget(status_label)

        # Рейтинг
        if manga_data.get('averageScore'):
            rating_label = Label(
                text=f"Рейтинг: {manga_data['averageScore']}%",
                font_size=dp(16),
                color=COLORS['text_dark'],
                halign='left'
            )
            info_layout.add_widget(rating_label)

        # Главы и тома
        details_text = ""
        if manga_data.get('chapters'):
            details_text += f"Глав: {manga_data['chapters']} "
        if manga_data.get('volumes'):
            details_text += f"Томов: {manga_data['volumes']}"

        if details_text:
            details_label = Label(
                text=details_text,
                font_size=dp(16),
                color=COLORS['text_dark'],
                halign='left'
            )
            info_layout.add_widget(details_label)

        # Кнопка добавления в библиотеку
        self.library_btn = Button(
            text='',
            size_hint_y=None,
            height=dp(40),
            background_color=COLORS['secondary'],
            color=[1, 1, 1, 1]
        )
        self.library_btn.bind(on_press=self.toggle_library)
        self.update_library_button()
        info_layout.add_widget(self.library_btn)

        # Кнопка "Читать на AniList"
        self.read_btn = Button(
            text=' Читать на AniList',
            size_hint_y=None,
            height=dp(40),
            background_color=[0.4, 0.2, 0.6, 1],
            color=[1, 1, 1, 1]
        )
        self.read_btn.bind(on_press=self.open_anilist)
        info_layout.add_widget(self.read_btn)

        cover_layout.add_widget(info_layout)
        self.content_layout.add_widget(cover_layout)

        # Жанры
        if manga_data.get('genres'):
            genres_text = " Жанры: " + ", ".join(manga_data['genres'])
            genres_label = Label(
                text=genres_text,
                font_size=dp(16),
                color=COLORS['text_dark'],
                halign='left',
                size_hint_y=None,
                height=dp(40)
            )
            self.content_layout.add_widget(genres_label)

        # Даты публикации
        dates_text = self.get_dates_text(manga_data)
        if dates_text:
            dates_label = Label(
                text=dates_text,
                font_size=dp(14),
                color=COLORS['text_dark'],
                halign='left',
                size_hint_y=None,
                height=dp(30)
            )
            self.content_layout.add_widget(dates_label)

        # Альтернативные названия
        if manga_data.get('synonyms'):
            synonyms_text = " Другие названия: " + ", ".join(manga_data['synonyms'][:3])
            synonyms_label = Label(
                text=synonyms_text,
                font_size=dp(14),
                color=COLORS['text_dark'],
                halign='left',
                size_hint_y=None,
                text_size=(Window.width - dp(20), None)
            )
            synonyms_label.bind(texture_size=lambda instance, size: setattr(synonyms_label, 'height', size[1] + dp(10)))
            self.content_layout.add_widget(synonyms_label)

        # Описание
        description = MangaAPI.clean_description(manga_data.get('description'))
        desc_label = Label(
            text=description,
            font_size=dp(14),
            color=COLORS['text_dark'],
            halign='left',
            size_hint_y=None,
            text_size=(Window.width - dp(20), None)
        )
        desc_label.bind(texture_size=lambda instance, size: setattr(desc_label, 'height', size[1] + dp(20)))
        self.content_layout.add_widget(desc_label)

        # Дополнительные ссылки
        links_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))

        # Кнопка поиска в Google
        google_btn = Button(
            text=' Поиск в Google',
            background_color=COLORS['primary'],
            color=[1, 1, 1, 1]
        )
        google_btn.bind(on_press=lambda x: self.search_google(manga_data))

        # Кнопка поиска перевода
        translation_btn = Button(
            text=' Поиск перевода',
            background_color=COLORS['secondary'],
            color=[1, 1, 1, 1]
        )
        translation_btn.bind(on_press=lambda x: self.search_translation(manga_data))

        links_layout.add_widget(google_btn)
        links_layout.add_widget(translation_btn)
        self.content_layout.add_widget(links_layout)

    def get_dates_text(self, manga_data):
        """Форматирует даты публикации"""
        start_date = manga_data.get('startDate', {})
        end_date = manga_data.get('endDate', {})

        start_text = ""
        end_text = ""

        if start_date.get('year'):
            start_text = f"{start_date.get('day', '?')}.{start_date.get('month', '?')}.{start_date['year']}"

        if end_date.get('year'):
            end_text = f"{end_date.get('day', '?')}.{end_date.get('month', '?')}.{end_date['year']}"

        if start_text and end_text:
            return f" Публикация: {start_text} - {end_text}"
        elif start_text:
            return f" Начало: {start_text}"
        else:
            return ""

    def open_anilist(self, instance):
        """Открывает мангу на AniList в браузере"""
        if self.current_manga_data and self.current_manga_data.get('siteUrl'):
            url = self.current_manga_data['siteUrl']
            try:
                webbrowser.open(url)
                self.show_message(f"Открываю AniList...")
            except Exception as e:
                self.show_message(f"Ошибка: Не удалось открыть браузер")
        else:
            # Если нет прямой ссылки, создаем поисковый запрос
            title = (self.current_manga_data['title']['romaji'] or
                     self.current_manga_data['title']['english'] or
                     '')
            if title:
                search_url = f"https://anilist.co/search/manga?search={title.replace(' ', '%20')}"
                try:
                    webbrowser.open(search_url)
                    self.show_message(f"Ищу '{title}' на AniList...")
                except Exception as e:
                    self.show_message(f"Ошибка: Не удалось открыть браузер")

    def search_google(self, manga_data):
        """Ищет мангу в Google"""
        title = manga_data['title']['romaji'] or manga_data['title']['english'] or 'манга'
        search_query = f"{title} манга"
        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '%20')}"

        try:
            webbrowser.open(search_url)
            self.show_message(f"Ищу в Google...")
        except Exception as e:
            self.show_message(f"Ошибка: Не удалось открыть браузер")

    def search_translation(self, manga_data):
        """Ищет перевод манги"""
        title = manga_data['title']['romaji'] or manga_data['title']['english'] or 'манга'
        search_query = f"{title} манга русский перевод"
        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '%20')}"

        try:
            webbrowser.open(search_url)
            self.show_message(f"Ищу перевод...")
        except Exception as e:
            self.show_message(f"Ошибка: Не удалось открыть браузер")

    def show_message(self, text):
        """Показывает временное сообщение"""
        content = Label(text=text, color=COLORS['text_dark'])
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.6, 0.2)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

    def update_library_button(self):
        """Обновляет текст кнопки добавления в библиотеку"""
        if not self.current_manga_id or not self.db.current_user_id:
            return

        is_in_library = self.db.is_in_library(self.db.current_user_id, self.current_manga_id)
        if is_in_library:
            self.library_btn.text = '🗑 Удалить из библиотеки'
            self.library_btn.background_color = COLORS['accent']
        else:
            self.library_btn.text = ' Добавить в библиотеку'
            self.library_btn.background_color = COLORS['secondary']

    def toggle_library(self, instance):
        """Добавляет или удаляет мангу из библиотеки"""
        logging.debug("=== TOGGLE LIBRARY ===")
        logging.debug(f"Manga ID: {self.current_manga_id}")
        logging.debug(f"User ID: {self.db.current_user_id}")
        logging.debug(f"Manga Data exists: {self.current_manga_data is not None}")

        if not self.current_manga_id:
            self.show_message("Ошибка: ID манги не установлен")
            return

        if not self.db.current_user_id:
            self.show_message("Ошибка: пользователь не авторизован")
            return

        if not self.current_manga_data:
            self.show_message("Ошибка: данные манги не загружены")
            return

        try:
            logging.debug("Проверяем наличие в библиотеке...")
            is_in_library = self.db.is_in_library(self.db.current_user_id, self.current_manga_id)
            logging.debug(f"В библиотеке: {is_in_library}")

            if is_in_library:
                # Удаляем из библиотеки
                logging.debug("Удаляем из библиотеки...")
                library = self.db.get_user_library(self.db.current_user_id)
                found = False
                for manga in library:
                    if manga[1] == self.current_manga_id:
                        logging.debug(f"Найдена запись: {manga[0]}")
                        success = self.db.remove_from_library(manga[0])
                        if success:
                            self.show_message("Удалено из библиотеки")
                            self.update_library_button()
                        else:
                            self.show_message("Ошибка удаления")
                        found = True
                        break

                if not found:
                    self.show_message("Запись не найдена в библиотеке")

            else:
                # Добавляем в библиотеку
                logging.debug("Добавляем в библиотеку...")
                title = (self.current_manga_data['title']['romaji'] or
                         self.current_manga_data['title']['english'] or
                         'Без названия')

                logging.debug(f"Название: {title}")

                cover_url = ""
                if self.current_manga_data.get('coverImage'):
                    cover_url = (self.current_manga_data['coverImage'].get('large') or
                                 self.current_manga_data['coverImage'].get('medium') or "")
                    logging.debug(f"Обложка: {cover_url[:50]}...")

                success, message = self.db.add_to_library(self.db.current_user_id, self.current_manga_id, title, "", cover_url)
                logging.debug(f"Результат: {success}, {message}")
                self.show_message(message)
                if success:
                    self.update_library_button()

        except Exception as e:
            logging.debug(f"Критическая ошибка в toggle_library: {e}")
            import traceback
            traceback.print_exc()
            self.show_message(f"Ошибка: {str(e)}")

    def show_error(self, error):
        self.content_layout.clear_widgets()
        error_label = Label(
            text=f'Ошибка: {error}',
            font_size=dp(16),
            color=COLORS['text_dark'],
            size_hint_y=None,
            height=dp(100)
        )
        self.content_layout.add_widget(error_label)

    def go_back(self, instance):
        """Возврат на предыдущий экран"""
        self.manager.current = 'search'
