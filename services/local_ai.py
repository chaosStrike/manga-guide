class LocalAI:
    @staticmethod
    def create_chat_completion(messages):
        user_question = messages[-1]["content"] if messages else ""
        return True, LocalAI.generate_response(user_question)

    @staticmethod
    def generate_response(question):
        question_lower = question.lower()

        knowledge_base = {
            'one piece': "One Piece - эпическая манга о пиратах. Более 1000 глав, все еще продолжается. Главный герой - Луффи, который хочет стать Королем Пиратов.",
            'naruto': "Naruto - классика о ниндзя. 700 глав, завершена. История Наруто Узумаки, который мечтает стать Хокаге.",
            'attack on titan': "Attack on Titan - мрачная манга о борьбе с титанами. Завершена, 139 глав. Очень драматичный сюжет.",
            'death note': "Death Note - психологический триллер о тетради смерти. 108 глав, завершена. Интеллектуальные дуэли.",
            'berserk': "Berserk - темное фэнтези. Незавершена, очень мрачная и глубокая история.",
            'романтика': "Лучшая романтическая манга:\n• Fruits Basket\n• Kimi ni Todoke\n• Horimiya\n• Wotakoi",
            'экшен': "Топ манга с экшеном:\n• One Piece\n• Naruto\n• Demon Slayer\n• Jujutsu Kaisen",
            'комедия': "Смешная манга:\n• Gintama\n• Grand Blue\n• Kaguya-sama",
            'новинки': "Популярная новая манга:\n• Chainsaw Man\n• Spy x Family\n• Oshi no Ko",
            'что почитать': "Рекомендую:\n• One Piece - долгие приключения\n• Death Note - интеллектуальный сюжет\n• Fullmetal Alchemist - баланс экшена и драмы\n• Attack on Titan - мрачные темы",
            'жанры': "Основные жанры:\n• Сёнен - для юношей\n• Сёдзе - для девушек\n• Сэйнэн - для взрослых\n• Кодомо - для детей"
        }

        for keyword, response in knowledge_base.items():
            if keyword in question_lower:
                return response

        return "Я могу порекомендовать мангу по жанрам, рассказать о популярных работах или объяснить термины. Спросите конкретнее!"