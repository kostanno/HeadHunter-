import json
import os
from abc import abstractmethod
from typing import List, Dict, Any
from src.vacanties import FileHandler, Vacancy


class JSONSaver(FileHandler):
    """Класс для сохранения вакансий в JSON файл"""

    def __init__(self, filename: str = "data/vacancies.json"):
        self.__filename = filename  # Приватный атрибут
        self._ensure_file_exists()

    @property
    def filename(self) -> str:
        """Геттер для имени файла (только чтение)"""
        return self.__filename

    def _ensure_file_exists(self) -> None:
        """Создание файла и директории, если они не существуют"""
        if not os.path.exists(self.__filename):
            with open(self.__filename, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _read_vacancies(self) -> List[Dict[str, str]]:
        """Чтение вакансий из файла"""
        try:
            with open(self.__filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Ошибка декодирования JSON в файле {self.__filename}")
            return []
        except FileNotFoundError:
            print(f"Файл {self.__filename} не найден")
            return []
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
            return []

    def _write_vacancies(self, vacancies: List[Dict[str, str]]) -> None:
        """Запись вакансий в файл"""
        try:
            with open(self.__filename, 'w', encoding='utf-8') as f:
                json.dump(vacancies, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при записи в файл: {e}")

    def add_vacancy(self, vacancy: Vacancy) -> None:
        """Добавление вакансии в файл"""
        vacancies = self._read_vacancies()
        vacancy_dict = vacancy.to_dict()
        existing_urls = {v.get('url') for v in vacancies}
        if vacancy_dict.get('url') not in existing_urls:
            vacancies.append(vacancy_dict)
            self._write_vacancies(vacancies)
            print(f"Вакансия '{vacancy.title}' добавлена")
        else:
            print(f"Вакансия с URL {vacancy_dict.get('url')} уже существует")

    def get_vacancies(self, criteria: Dict[str, Any]) -> List[Vacancy]:
        """Получение вакансий по критериям"""
        all_vacancies_data = self._read_vacancies()
        filtered_vacancies = []
        for vacancy_data in all_vacancies_data:
            if self._matches_criteria(vacancy_data, criteria):
                try:
                    filtered_vacancies.append(Vacancy.from_dict(vacancy_data))
                except Exception as e:
                    print(f"Ошибка при создании вакансии из данных: {e}")
                    continue
        return filtered_vacancies

    def _matches_criteria(self, vacancy_data: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Проверяет, соответствует ли вакансия критериям"""
        for key, value in criteria.items():
            vacancy_value = vacancy_data.get(key, '').lower()
            if key == 'salary':
                if value == 'with_salary':
                    if vacancy_value == 'зарплата не указана':
                        return False
                elif value == 'without_salary':
                    if vacancy_value != 'зарплата не указана':
                        return False
            elif key == 'keyword':
                search_value = value.lower()
                title = vacancy_data.get('title', '').lower()
                description = vacancy_data.get('description', '').lower()
                if (search_value not in title and search_value not in description):
                    return False
            elif key == 'min_salary':
                try:
                    vacancy_salary = vacancy_data.get('salary', '')
                    if vacancy_salary == 'Зарплата не указана':
                        return False
                    salary_parts = vacancy_salary.split()
                    min_salary_vacancy = 0
                    for part in salary_parts:
                        cleaned_part = ''.join(filter(str.isdigit, part))
                        if cleaned_part:
                            min_salary_vacancy = int(cleaned_part)
                            break
                    if min_salary_vacancy < value:
                        return False
                except (ValueError, IndexError):
                    return False
            else:
                if value.lower() not in vacancy_value:
                    return False
        return True

    def delete_vacancy(self, vacancy: Vacancy) -> None:
        """Удаление вакансии из файла"""
        vacancies = self._read_vacancies()
        vacancy_dict = vacancy.to_dict()
        initial_count = len(vacancies)
        vacancies = [v for v in vacancies if v.get('url') != vacancy_dict.get('url')]
        if len(vacancies) < initial_count:
            self._write_vacancies(vacancies)
            print(f"Вакансия '{vacancy.title}' удалена")
        else:
            print("Вакансия не найдена")

    def clear_all(self) -> None:
        """Очистка всех вакансий"""
        self._write_vacancies([])
        print("Все вакансии удалены")

    def get_all_vacancies(self) -> List[Vacancy]:
        """Получение всех вакансий из файла"""
        vacancies_data = self._read_vacancies()
        vacancies = []
        for data in vacancies_data:
            try:
                vacancies.append(Vacancy.from_dict(data))
            except Exception as e:
                print(f"Ошибка при создании вакансии: {e}")
                continue
        return vacancies

    def count_vacancies(self) -> int:
        """Возвращает количество вакансий в файле"""
        return len(self._read_vacancies())


def filter_vacancies(vacancies: List[Vacancy], filter_words: List[str]) -> List[Vacancy]:
    """Фильтрация вакансий по ключевым словам"""
    if not filter_words:
        return vacancies
    filtered = []
    for vacancy in vacancies:
        description = f"{vacancy.title} {vacancy.description}".lower()
        if any(word.lower() in description for word in filter_words if word.strip()):
            filtered.append(vacancy)
    return filtered


def get_vacancies_by_salary(vacancies: List[Vacancy], salary_range: str) -> List[Vacancy]:
    """Фильтрация вакансий по диапазону зарплат"""
    if not salary_range:
        return vacancies
    try:
        if '-' in salary_range:
            min_salary, max_salary = map(int, salary_range.split('-'))
        else:
            min_salary = int(salary_range)
            max_salary = float('inf')
        filtered = []
        for vacancy in vacancies:
            salary_num = vacancy.get_salary_numeric()
            if min_salary <= salary_num <= max_salary:
                filtered.append(vacancy)
        return filtered
    except ValueError:
        print("Неверный формат диапазона зарплат. Используйте формат: 100000-150000 или 100000")
        return vacancies


def sort_vacancies(vacancies: List[Vacancy]) -> List[Vacancy]:
    """Сортировка вакансий по зарплате (по убыванию)"""
    return sorted(vacancies, reverse=True)


def get_top_vacancies(vacancies: List[Vacancy], top_n: int) -> List[Vacancy]:
    """Получение топ N вакансий"""
    if top_n <= 0:
        return vacancies
    return vacancies[:top_n]


def print_vacancies(vacancies: List[Vacancy]) -> None:
    """Вывод вакансий в консоль"""
    if not vacancies:
        print("Вакансии не найдены.")
        return
    print(f"\nНайдено вакансий: {len(vacancies)}")
    for i, vacancy in enumerate(vacancies, 1):
        print(f"\n{'=' * 60}")
        print(f"ВАКАНСИЯ #{i}")
        print(f"{'=' * 60}")
        print(vacancy)
