import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class VacancyAPI(ABC):
    """Абстрактный класс для работы с API сервисов вакансий"""

    @abstractmethod
    def get_vacancies(self, search_query: str) -> List[Dict[str, Any]]:
        pass


class HeadHunterAPI(VacancyAPI):
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self.__base_url = "https://api.hh.ru/vacancies"
        self.__timeout = 10  #для запросов

    def __connect_to_api(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Приватный метод для подключения к API"""
        try:
            response = requests.get(self.__base_url, params=params, timeout=self.__timeout)
            response.raise_for_status() #добавил проверку статус кода
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API HeadHunter: {e}")
            return None

    def get_vacancies(self, search_query: str, area: str = "113") -> List[Dict[str, Any]]:
        """Получение вакансий с hh.ru"""
        params = {
            'text': search_query,
            'area': area,
            'page': 0
        }
        data = self.__connect_to_api(params)
        return data.get('items', [])