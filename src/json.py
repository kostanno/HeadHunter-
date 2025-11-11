import json
import os
from typing import List, Dict, Any
from src.vacanties import FileHandler, Vacancy


class JSONDecodeError:
    pass


class JSONSaver(FileHandler):
    """Класс для сохранения вакансий в JSON файл"""

    def __init__(self, filename: str = "data/vacancies.json"):
        self.filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Создание файла, если он не существует"""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _read_vacancies(self) -> List[Dict[str, str]]:
        """Чтение вакансий из файла"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_vacancies(self, vacancies: List[Dict[str, str]]) -> None:
        """Запись вакансий в файл"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(vacancies, f, ensure_ascii=False, indent=2)

    def add_vacancy(self, vacancy: Vacancy) -> None:
        """Добавление вакансии в файл"""
        vacancies = self._read_vacancies()
        vacancy_dict = vacancy.to_dict()
        if vacancy_dict not in vacancies:
            vacancies.append(vacancy_dict)
            self._write_vacancies(vacancies)

    def get_vacancies(self, criteria: Dict[str, Any]) -> List[Vacancy]:
        """Получение вакансий по критериям"""
        all_vacancies_data = self._read_vacancies()
        filtered_vacancies = []
        for vacancy_data in all_vacancies_data:
            matches = True
            for key, value in criteria.items():
                vacancy_value = vacancy_data.get(key, '').lower()
                if key == 'salary':
                    if value == 'with_salary':
                        if vacancy_value == 'зарплата не указана':
                            matches = False
                            break
                    elif value == 'without_salary':
                        if vacancy_value != 'зарплата не указана':
                            matches = False
                            break
                elif key == 'keyword':
                    search_value = value.lower()
                    if (search_value not in vacancy_data.get('title', '').lower() and
                            search_value not in vacancy_data.get('description', '').lower()):
                        matches = False
                        break
                elif key == 'min_salary':
                    try:
                        vacancy_salary = vacancy_data.get('salary', '')
                        if vacancy_salary != 'Зарплата не указана':
                            salary_parts = vacancy_salary.split()
                            min_salary_vacancy = 0
                            for part in salary_parts:
                                if part.isdigit():
                                    min_salary_vacancy = int(part)
                                    break
                            if min_salary_vacancy < value:
                                matches = False
                                break
                        else:
                            matches = False
                            break
                    except (ValueError, IndexError):
                        matches = False
                        break
                else:
                    if value.lower() not in vacancy_value:
                        matches = False
                        break
            if matches:
                filtered_vacancies.append(Vacancy.from_dict(vacancy_data))
        return filtered_vacancies

    def delete_vacancy(self, vacancy: Vacancy) -> None:
        """Удаление вакансии из файла"""
        vacancies = self._read_vacancies()
        vacancy_dict = vacancy.to_dict()

        if vacancy_dict in vacancies:
            vacancies.remove(vacancy_dict)
            self._write_vacancies(vacancies)

    def clear_all(self) -> None:
        """Очистка всех вакансий"""
        self._write_vacancies([])


def filter_vacancies(vacancies: List[Vacancy], filter_words: List[str]) -> List[Vacancy]:
    """Фильтрация вакансий по ключевым словам"""
    if not filter_words:
        return vacancies
    filtered = []
    for vacancy in vacancies:
        description = f"{vacancy.title} {vacancy.description}".lower()
        if any(word.lower() in description for word in filter_words):
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
        print("Неверный формат диапазона зарплат")
        return vacancies


def sort_vacancies(vacancies: List[Vacancy]) -> List[Vacancy]:
    """Сортировка вакансий по зарплате (по убыванию)"""
    return sorted(vacancies)


def get_top_vacancies(vacancies: List[Vacancy], top_n: int) -> List[Vacancy]:
    """Получение топ N вакансий"""
    return vacancies[:top_n]


def print_vacancies(vacancies: List[Vacancy]) -> None:
    """Вывод вакансий в консоль"""
    if not vacancies:
        print("Вакансии не найдены.")
        return

    for i, vacancy in enumerate(vacancies, 1):
        print(f"\n{'=' * 50}")
        print(f"Вакансия #{i}")
        print(f"{'=' * 50}")
        print(vacancy)
