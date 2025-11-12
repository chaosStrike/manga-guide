from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

from .base_screen import BackgroundScreen
from services import Database
from utils.constants import COLORS, READING_STATUSES


class LibraryScreen(BackgroundScreen):
    def __init__(self, db=None, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.clear_widgets()

        self.current_filter = None

        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс библиотеки"""
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Верхняя панель
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))

        back_btn = Button(
            text='Назад',
            background_color=COLORS['primary'],
            size_hint_x=None,
            width=dp(100),
            font_size=dp(16),
            color=[1, 1, 1, 1]
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))

        self.title_label = Label(
            text='Моя библиотека',
            font_size=dp(18),
            color=COLORS['text_dark'],
            halign='left'
        )

        add_btn = Button(
            text='+ Добавить',
            size_hint_x=None,
            width=dp(100),
            background_color=COLORS['secondary'],
            font_size=dp(14),
            color=[1, 1, 1, 1]
        )
        add_btn.bind(on_press=self.show_add_dialog)

        top_layout.add_widget(back_btn)
        top_layout.add_widget(self.title_label)
        top_layout.add_widget(add_btn)

        layout.add_widget(top_layout)

        # Панель фильтров статусов
        self.filters_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(5)
        )
        self.create_status_filters()
        layout.add_widget(self.filters_layout)

        # Статистика
        self.stats_label = Label(
            text='',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(12),
            color=COLORS['text_dark']
        )
        layout.add_widget(self.stats_label)

        # Список манги
        self.library_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(10)
        )
        self.library_layout.bind(minimum_height=self.library_layout.setter('height'))

        self.scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )
        self.scroll.add_widget(self.library_layout)
        layout.add_widget(self.scroll)

        self.add_widget(layout)

    def create_status_filters(self):
        """Создает кнопки фильтров по статусам"""
        self.filters_layout.clear_widgets()

        # Кнопка "Все"
        all_btn = Button(
            text='Все',
            size_hint_x=1,
            background_color=COLORS['primary'],
            font_size=dp(12),
            color=[1, 1, 1, 1]
        )
        all_btn.bind(on_press=lambda x: self.filter_by_status(None))
        self.filters_layout.add_widget(all_btn)

        # Кнопки статусов
        for status_key, status_text in READING_STATUSES.items():
            btn = Button(
                text=status_text,
                size_hint_x=1,
                background_color=[0.7, 0.7, 0.7, 1],
                font_size=dp(11),
                color=COLORS['text_dark']
            )
            btn.bind(on_press=lambda x, s=status_key: self.filter_by_status(s))
            self.filters_layout.add_widget(btn)

    def filter_by_status(self, status):
        """Фильтрует библиотеку по статусу"""
        self.current_filter = status
        self.update_filter_buttons()
        self.load_library()
        self.update_stats()

    def update_filter_buttons(self):
        """Обновляет цвета кнопок фильтров"""
        for i, child in enumerate(self.filters_layout.children):
            if i == 0:  # Кнопка "Все"
                if self.current_filter is None:
                    child.background_color = COLORS['primary']
                else:
                    child.background_color = [0.7, 0.7, 0.7, 1]
            else:
                status_key = list(READING_STATUSES.keys())[i - 1]
                if self.current_filter == status_key:
                    child.background_color = COLORS['secondary']
                else:
                    child.background_color = [0.7, 0.7, 0.7, 1]

    def update_stats(self):
        """Обновляет статистику библиотеки"""
        if not self.db.current_user_id:
            return

        stats = self.db.get_library_stats(self.db.current_user_id)

        stats_text = "Всего: {}".format(stats.get('total', 0))
        for status_key, status_text in READING_STATUSES.items():
            count = stats.get(status_key, 0)
            if count > 0:
                stats_text += f" | {status_text}: {count}"

        self.stats_label.text = stats_text

    def on_pre_enter(self):
        self.load_library()
        self.update_stats()

    def load_library(self):
        self.library_layout.clear_widgets()

        user_id = self.db.current_user_id
        if not user_id:
            empty_label = Label(
                text='Ошибка: пользователь не авторизован',
                font_size=dp(16),
                halign='center',
                color=COLORS['text_dark']
            )
            self.library_layout.add_widget(empty_label)
            return

        library = self.db.get_user_library(user_id, self.current_filter)

        if not library:
            status_text = READING_STATUSES.get(self.current_filter, '') if self.current_filter else ''
            filter_text = f" {status_text}" if status_text else ""

            empty_label = Label(
                text=f'Библиотека{filter_text} пуста\nНажмите "+ Добавить" чтобы добавить мангу',
                font_size=dp(16),
                halign='center',
                color=COLORS['text_dark']
            )
            self.library_layout.add_widget(empty_label)
            return

        for manga in library:
            manga_id, manga_api_id, title, author, status, rating, cover_url, notes, progress, total_chapters = manga
            manga_card = self.create_manga_card(manga_id, manga_api_id, title, author, status, cover_url, progress,
                                                total_chapters)
            self.library_layout.add_widget(manga_card)

    def create_manga_card(self, db_id, manga_api_id, title, author, status, cover_url, progress=0, total_chapters=0):
        card = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(120),
            padding=dp(10),
            spacing=dp(10)
        )

        # Обложка
        if cover_url:
            cover = AsyncImage(
                source=cover_url,
                size_hint_x=None,
                width=dp(80),
                nocache=True
            )
            card.add_widget(cover)
        else:
            no_cover = Label(
                text='Нет обложки',
                font_size=dp(12),
                color=COLORS['text_dark'],
                size_hint_x=None,
                width=dp(80)
            )
            card.add_widget(no_cover)

        # Информация
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.6)

        title_label = Label(
            text=title,
            font_size=dp(16),
            halign='left',
            size_hint_y=0.6,
            color=COLORS['text_dark'],
            text_size=(Window.width * 0.5, None)
        )

        # Прогресс чтения
        progress_text = ""
        if progress > 0 and total_chapters > 0:
            progress_percent = int((progress / total_chapters) * 100)
            progress_text = f"Прогресс: {progress}/{total_chapters} ({progress_percent}%)"
        elif progress > 0:
            progress_text = f"Прогресс: глава {progress}"

        details_text = f"{READING_STATUSES.get(status, 'Читаю')}"
        if progress_text:
            details_text += f"\n{progress_text}"

        details_label = Label(
            text=details_text,
            font_size=dp(12),
            halign='left',
            size_hint_y=0.4,
            color=COLORS['text_dark']
        )

        info_layout.add_widget(title_label)
        info_layout.add_widget(details_label)
        card.add_widget(info_layout)

        # Кнопки управления
        buttons_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(100), spacing=dp(5))

        # Кнопка смены статуса
        status_btn = Button(
            text='Статус',
            size_hint_y=None,
            height=dp(35),
            background_color=COLORS['primary'],
            font_size=dp(12)
        )
        status_btn.bind(on_press=lambda x, mid=db_id: self.show_status_popup(mid, status))

        # Кнопка прогресса
        progress_btn = Button(
            text='Прогресс',
            size_hint_y=None,
            height=dp(35),
            background_color=COLORS['secondary'],
            font_size=dp(12)
        )
        progress_btn.bind(
            on_press=lambda x, mid=db_id, t=title, p=progress, tc=total_chapters:
            self.show_progress_popup(mid, t, p, tc)
        )

        # Кнопка удаления
        delete_btn = Button(
            text='Удалить',
            size_hint_y=None,
            height=dp(35),
            background_color=COLORS['accent'],
            font_size=dp(12)
        )
        delete_btn.bind(on_press=lambda x, mid=db_id: self.remove_manga(mid))

        buttons_layout.add_widget(status_btn)
        buttons_layout.add_widget(progress_btn)
        buttons_layout.add_widget(delete_btn)

        card.add_widget(buttons_layout)

        return card

    def show_status_popup(self, library_id, current_status):
        """Показывает попап для смены статуса"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        content.add_widget(Label(text='Выберите статус:', font_size=dp(16), color=COLORS['text_dark']))

        for status_key, status_text in READING_STATUSES.items():
            btn = Button(
                text=status_text,
                background_color=COLORS['secondary'] if status_key == current_status else COLORS['primary'],
                color=[1, 1, 1, 1]
            )
            btn.bind(on_press=lambda x, s=status_key: self.change_status(library_id, s, popup))
            content.add_widget(btn)

        popup = Popup(title='Смена статуса', content=content, size_hint=(0.8, 0.6))
        popup.open()

    def change_status(self, library_id, new_status, popup):
        """Меняет статус манги"""
        success = self.db.update_manga_status(library_id, new_status)
        if success:
            popup.dismiss()
            self.load_library()
            self.update_stats()

    def show_progress_popup(self, library_id, title, current_progress, total_chapters):
        """Показывает попап для изменения прогресса"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        content.add_widget(Label(text=f'Прогресс: {title}', font_size=dp(16), color=COLORS['text_dark']))

        # Поле для текущей главы
        progress_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        progress_layout.add_widget(Label(text='Текущая глава:', color=COLORS['text_dark']))
        progress_input = TextInput(
            text=str(current_progress),
            size_hint_x=0.3,
            foreground_color=COLORS['text_dark'],
            background_color=[1, 1, 1, 1]
        )
        progress_layout.add_widget(progress_input)
        content.add_widget(progress_layout)

        # Поле для общего количества глав
        total_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        total_layout.add_widget(Label(text='Всего глав:', color=COLORS['text_dark']))
        total_input = TextInput(
            text=str(total_chapters) if total_chapters else '',
            size_hint_x=0.3,
            foreground_color=COLORS['text_dark'],
            background_color=[1, 1, 1, 1],
            hint_text='0'
        )
        total_layout.add_widget(total_input)
        content.add_widget(total_layout)

        # Кнопки
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))

        def save_progress(btn):
            try:
                progress = int(progress_input.text) if progress_input.text else 0
                total = int(total_input.text) if total_input.text else 0
                success = self.db.update_manga_progress(library_id, progress, total if total > 0 else None)
                if success:
                    popup.dismiss()
                    self.load_library()
            except ValueError:
                pass

        save_btn = Button(text='Сохранить', background_color=COLORS['secondary'])
        save_btn.bind(on_press=save_progress)

        cancel_btn = Button(text='Отмена', background_color=COLORS['accent'])
        cancel_btn.bind(on_press=lambda x: popup.dismiss())

        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(title='Прогресс чтения', content=content, size_hint=(0.8, 0.5))
        popup.open()

    def show_add_dialog(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        content.add_widget(Label(text='Добавить мангу', font_size=dp(20), color=COLORS['text_dark']))

        title_input = TextInput(
            hint_text='Название манги *',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16),
            foreground_color=COLORS['text_dark'],
            background_color=[1, 1, 1, 1]
        )
        author_input = TextInput(
            hint_text='Автор (необязательно)',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16),
            foreground_color=COLORS['text_dark'],
            background_color=[1, 1, 1, 1]
        )

        content.add_widget(title_input)
        content.add_widget(author_input)

        msg_label = Label(text='', size_hint_y=None, height=dp(30), color=COLORS['text_dark'])
        content.add_widget(msg_label)

        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        def add_manga(btn):
            title = title_input.text.strip()
            author = author_input.text.strip()

            if not title:
                msg_label.text = "Введите название манги"
                return

            success, message = self.db.add_to_library(self.db.current_user_id, 0, title, author)
            msg_label.text = message
            if success:
                Clock.schedule_once(lambda dt: popup.dismiss(), 1)
                self.load_library()

        def cancel(btn):
            popup.dismiss()

        add_btn = Button(
            text='Добавить',
            background_color=COLORS['secondary'],
            color=[1, 1, 1, 1]
        )
        add_btn.bind(on_press=add_manga)

        cancel_btn = Button(
            text='Отмена',
            background_color=COLORS['accent'],
            color=[1, 1, 1, 1]
        )
        cancel_btn.bind(on_press=cancel)

        btn_layout.add_widget(add_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.5)
        )
        popup.open()

    def remove_manga(self, manga_id):
        success = self.db.remove_from_library(manga_id)
        if success:
            self.load_library()
