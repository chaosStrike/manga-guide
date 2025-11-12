
import requests
import html
import re

class MangaAPI:
    @staticmethod
    def search_manga(query, page=1, per_page=20):
        """Поиск манги через AniList GraphQL API"""
        url = 'https://graphql.anilist.co'

        graphql_query = '''
        query ($search: String, $page: Int, $perPage: Int) {
            Page(page: $page, perPage: $perPage) {
                pageInfo {
                    total
                    currentPage
                    lastPage
                    hasNextPage
                }
                media(search: $search, type: MANGA, sort: POPULARITY_DESC) {
                    id
                    title {
                        romaji
                        english
                    }
                    description
                    coverImage {
                        large
                        medium
                    }
                    status
                    chapters
                    volumes
                    averageScore
                    genres
                }
            }
        }
        '''

        variables = {
            'search': query,
            'page': page,
            'perPage': per_page
        }

        try:
            response = requests.post(
                url,
                json={'query': graphql_query, 'variables': variables},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'Page' in data['data']:
                    return data['data']['Page']
                else:
                    print("API Response error:", data)
                    return {'media': [], 'pageInfo': {}}
            else:
                print(f"API Error: {response.status_code}")
                return {'media': [], 'pageInfo': {}}

        except Exception as e:
            print(f"API Request Error: {e}")
            return {'media': [], 'pageInfo': {}}

    @staticmethod
    def get_manga_by_id(manga_id):
        """Получение информации о манге по ID"""
        url = 'https://graphql.anilist.co'

        graphql_query = '''
        query ($id: Int) {
            Media(id: $id, type: MANGA) {
                id
                title {
                    romaji
                    english
                }
                description
                coverImage {
                    large
                    extraLarge
                    medium
                }
                status
                chapters
                volumes
                averageScore
                genres
                startDate {
                    year
                    month
                    day
                }
                endDate {
                    year
                    month
                    day
                }
                synonyms
                siteUrl
            }
        }
        '''

        variables = {
            'id': manga_id
        }

        try:
            response = requests.post(
                url,
                json={'query': graphql_query, 'variables': variables},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'Media' in data['data']:
                    return data['data']['Media']
                else:
                    print("API Response error:", data)
                    return None
            else:
                print(f"API Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"API Request Error: {e}")
            return None

    @staticmethod
    def clean_description(description):
        """Очищает описание от HTML тегов"""
        if not description:
            return "Описание отсутствует"

        clean_text = html.unescape(description)
        clean_text = clean_text.replace('<br>', '\n')
        clean_text = clean_text.replace('<i>', '').replace('</i>', '')
        clean_text = clean_text.replace('<b>', '').replace('</b>', '')
        clean_text = re.sub(r'<[^>]+>', '', clean_text)

        if len(clean_text) > 500:
            clean_text = clean_text[:500] + "..."

        return clean_text