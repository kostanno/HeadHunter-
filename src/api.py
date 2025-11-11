import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class VacancyAPI(ABC):
    """Абстрактный класс для работы с API сервисов вакансий"""

    @abstractmethod
    def get_vacancies(self, search_query: str) -> List[Dict[str, Any]]:
        pass


class HeadHunterAPI(VacancyAPI):
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self.base_url = "https://api.hh.ru/vacancies"

    def get_vacancies(self, search_query: str, area: str = "113") -> List[Dict[str, Any]]:
        """Получение вакансий с hh.ru"""
        params = {
            'text': search_query,
            'area': area,
            'per_page': 100
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('items', [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            return []
