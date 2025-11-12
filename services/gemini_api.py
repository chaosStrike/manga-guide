import requests


class GeminiAPI:
    @staticmethod
    def create_chat_completion(messages):
        """Отправляет запрос к бесплатным Gemini прокси"""
        proxies = [
            "https://gemini-proxy.fly.dev/v1/chat/completions",
            "https://api.gemini-chat.pro/v1/chat/completions",
        ]

        payload = {
            "model": "gemini-pro",
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7
        }

        for proxy_url in proxies:
            try:
                response = requests.post(proxy_url, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data and data["choices"]:
                        return True, data["choices"][0]["message"]["content"]
            except Exception as e:
                continue  # Пробуем следующий прокси

        return False, "Все прокси недоступны"