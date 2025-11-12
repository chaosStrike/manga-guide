
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

from .base_screen import BackgroundScreen
from services import MangaAPI
from utils.constants import COLORS
import logging

class SearchScreen(BackgroundScreen):
    def __init__(self, db=None, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.clear_widgets()

        self.current_page = 1
        self.current_query = ""
        self.has_next_page = False

        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс поиска"""
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Верхняя панель: кнопка назад и поисковая строка
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))

        # Кнопка назад
        back_btn = Button(
            text=' Назад',
            background_color=COLORS['primary'],
            size_hint_x=None,
            width=dp(100),
            font_size=dp(16),
            color=[1, 1, 1, 1]
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))

        # Поисковая строка
        self.search_input = TextInput(
            hint_text='Введите название манги...',
            font_size=dp(16),
            foreground_color=COLORS['text_dark'],
            background_color=[1, 1, 1, 1]
        )
        search_btn = Button(
            text='Поиск',
            size_hint_x=None,
            width=dp(60),
            background_color=COLORS['secondary'],
            color=[1, 1, 1, 1]
        )
        search_btn.bind(on_press=self.do_search)

        top_layout.add_widget(back_btn)
        top_layout.add_widget(self.search_input)
        top_layout.add_widget(search_btn)
        layout.add_widget(top_layout)

        # Результаты поиска
        self.results_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        # ВАЖНО: Привязка высоты контента к содержимому
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))

        self.scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(10)
        )
        self.scroll.add_widget(self.results_layout)
        layout.add_widget(self.scroll)

        # Пагинация
        self.pagination_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(5)
        )

        self.prev_btn = Button(
            text='⬅',
            size_hint_x=None,
            width=dp(60),
            background_color=COLORS['primary'],
            color=[1, 1, 1, 1]
        )
        self.prev_btn.bind(on_press=self.prev_page)

        self.page_label = Label(
            text='1',
            color=COLORS['text_dark'],
            size_hint_x=1
        )

        self.next_btn = Button(
            text='➡',
            size_hint_x=None,
            width=dp(60),
            background_color=COLORS['primary'],
            color=[1, 1, 1, 1]
        )
        self.next_btn.bind(on_press=self.next_page)

        self.pagination_layout.add_widget(self.prev_btn)
        self.pagination_layout.add_widget(self.page_label)
        self.pagination_layout.add_widget(self.next_btn)

        layout.add_widget(self.pagination_layout)
        self.update_pagination_buttons()

        self.add_widget(layout)

    def do_search(self, instance):
        query = self.search_input.text.strip()
        if not query:
            return

        self.current_query = query
        self.current_page = 1
        self.perform_search(query, 1)

    def perform_search(self, query, page):
        self.results_layout.clear_widgets()
        loading_label = Label(
            text='Идет поиск...',
            font_size=dp(16),
            color=COLORS['text_dark'],
            size_hint_y=None,
            height=dp(40)
        )
        self.results_layout.add_widget(loading_label)

        def search_thread(dt):
            try:
                result = MangaAPI.search_manga(query, page=page, per_page=20)
                Clock.schedule_once(lambda dt: self.show_results(result), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_error(str(e)), 0)

        Clock.schedule_once(search_thread, 0.1)

    def show_error(self, error):
        self.results_layout.clear_widgets()
        error_label = Label(
            text=f'Ошибка поиска: {error}',
            font_size=dp(16),
            color=COLORS['text_dark'],
            size_hint_y=None,
            height=dp(40)
        )
        self.results_layout.add_widget(error_label)

    def show_results(self, result):
        self.results_layout.clear_widgets()

        media_list = result.get('media', [])
        page_info = result.get('pageInfo', {})

        self.has_next_page = page_info.get('hasNextPage', False)
        self.current_page = page_info.get('currentPage', 1)

        self.update_pagination_buttons()

        if not media_list:
            no_results = Label(
                text='Ничего не найдено\nПопробуйте другой запрос',
                font_size=dp(16),
                color=COLORS['text_dark'],
                size_hint_y=None,
                height=dp(80)
            )
            self.results_layout.add_widget(no_results)
            return

        for manga in media_list:
            manga_card = self.create_manga_card(manga)
            self.results_layout.add_widget(manga_card)

    def update_pagination_buttons(self):
        self.page_label.text = f'{self.current_page}'
        self.prev_btn.disabled = (self.current_page <= 1)
        self.next_btn.disabled = not self.has_next_page

        self.prev_btn.background_color = COLORS['primary'] if self.current_page > 1 else [0.5, 0.5, 0.5, 1]
        self.next_btn.background_color = COLORS['primary'] if self.has_next_page else [0.5, 0.5, 0.5, 1]

    def prev_page(self, instance):
        if self.current_page > 1:
            self.current_page -= 1
            self.perform_search(self.current_query, self.current_page)

    def next_page(self, instance):
        if self.has_next_page:
            self.current_page += 1
            self.perform_search(self.current_query, self.current_page)

    def create_manga_card(self, manga):
        card = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(100),
            padding=dp(5),
            spacing=dp(5)
        )

        # Обложка
        cover_url = None
        if manga.get('coverImage'):
            cover_url = manga['coverImage'].get('large') or manga['coverImage'].get('medium')

        if cover_url:
            cover = AsyncImage(
                source=cover_url,
                size_hint_x=None,
                width=dp(70),
                nocache=True
            )
            card.add_widget(cover)
        else:
            no_cover = Label(
                text='Нет\nобложки',
                font_size=dp(10),
                color=COLORS['text_dark'],
                size_hint_x=None,
                width=dp(70)
            )
            card.add_widget(no_cover)

        # Информация
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.75)

        title = manga['title']['romaji'] or manga['title']['english'] or 'Без названия'
        title_label = Label(
            text=title,
            font_size=dp(14),
            halign='left',
            size_hint_y=0.6,
            color=COLORS['text_dark'],
            text_size=(Window.width * 0.6, None)
        )

        # Детали
        details = ""
        if manga.get('status'):
            status_ru = {
                'FINISHED': 'Завершена',
                'RELEASING': 'Выходит',
                'NOT_YET_RELEASED': 'Не вышла',
                'CANCELLED': 'Отменена',
                'HIATUS': 'Заморожена'
            }
            status = status_ru.get(manga['status'], manga['status'])
            details += f"{status}"

        if manga.get('averageScore'):
            if details:
                details += " • "
            details += f"{manga['averageScore']}%"

        details_label = Label(
            text=details,
            font_size=dp(12),
            halign='left',
            size_hint_y=0.4,
            color=COLORS['text_dark']
        )

        info_layout.add_widget(title_label)
        info_layout.add_widget(details_label)

        # Кнопка перехода на детальную страницу
        detail_btn = Button(
            text='book',  # Иконка книги
            size_hint_x=None,
            width=dp(40),
            background_color=COLORS['primary'],
            font_size=dp(12),
            color=[1, 1, 1, 1]
        )
        detail_btn.bind(on_press=lambda x: self.show_manga_details(manga))

        card.add_widget(info_layout)
        card.add_widget(detail_btn)

        return card

    def show_manga_details(self, manga):
        """Переход на детальную страницу манги"""
        manga_id = manga['id']
        self.manager.get_screen('manga_detail').load_manga(manga_id)
        self.manager.current = 'manga_detail'