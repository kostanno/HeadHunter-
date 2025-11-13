from abc import abstractmethod, ABC
from typing import List, Dict, Any, Optional


class Vacancy:
    """Класс для представления вакансии"""

    __slots__ = ('__title', '__url', '__salary', '__description')

    def __init__(self, title: str, url: str, salary: Optional[Dict], description: str):
        self.__title = self.__validate_title(title)
        self.__url = self.__validate_url(url)
        self.__salary = self.__validate_salary(salary)
        self.__description = self.__validate_description(description)

    def __validate_title(self, title: str) -> str:
        """Валидация названия вакансии"""
        if not title or not isinstance(title, str):
            return "Название не указано"
        return title

    def __validate_url(self, url: str) -> str:
        """Валидация URL"""
        if not url or not isinstance(url, str):
            return "URL не указан"
        return url

    def __validate_salary(self, salary) -> str:
        """Валидация и форматирование зарплаты"""
        if not salary:
            return "Зарплата не указана"

        try:
            salary_from = salary.get('from')
            salary_to = salary.get('to')
            currency = salary.get('currency', 'RUR')

            if salary_from and salary_to:
                return f"{salary_from} - {salary_to} {currency}"
            elif salary_from:
                return f"от {salary_from} {currency}"
            elif salary_to:
                return f"до {salary_to} {currency}"
            else:
                return "Зарплата не указана"
        except (AttributeError, TypeError):
            return "Зарплата не указана"

    def __validate_description(self, description: str) -> str:
        """Валидация описания"""
        if not description or not isinstance(description, str):
            return "Описание не указано"

    @property
    def title(self) -> str:
        return self.__title

    @property
    def url(self) -> str:
        return self.__url

    @property
    def salary(self) -> str:
        return self.__salary

    @property
    def description(self) -> str:
        return self.__description

    def get_salary_numeric(self) -> int:
        """Получение числового значения зарплаты для сравнения"""
        if self.__salary == "Зарплата не указана":
            return 0

        try:
            salary_text = self.__salary.split()[0]
            if salary_text == 'от':
                salary_text = self.__salary.split()[1]
            elif salary_text == 'до':
                salary_text = self.__salary.split()[1]
            salary_text = ''.join(filter(str.isdigit, salary_text))
            return int(salary_text) if salary_text else 0
        except (ValueError, IndexError, AttributeError):
            return 0

    def __eq__(self, other):
        if not isinstance(other, Vacancy):
            return False
        return self.get_salary_numeric() == other.get_salary_numeric()

    def __str__(self) -> str:
        return (f"Вакансия: {self.title}\n"
                f"Зарплата: {self.salary}\n"
                f"Ссылка: {self.url}\n"
                f"Описание: {self.description[:200]}...\n")

    def to_dict(self) -> Dict[str, str]:
        """Преобразование вакансии в словарь для сохранения"""
        return {
            'title': self.title,
            'url': self.url,
            'salary': self.salary,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Vacancy':
        """Создание вакансии из словаря"""
        return cls(
            title=data.get('title', ''),
            url=data.get('url', ''),
            salary={'from': None, 'to': None, 'currency': 'RUR'},
            description=data.get('description', '')
        )

    @classmethod
    def cast_to_object_list(cls, vacancies_data: List[Dict[str, Any]]) -> List['Vacancy']:
        """Преобразование JSON данных в список объектов Vacancy"""
        vacancies = []
        for vacancy_data in vacancies_data:
            try:
                salary_info = vacancy_data.get('salary')
                snippet = vacancy_data.get('snippet', {})
                description = f"{snippet.get('requirement', '')} {snippet.get('responsibility', '')}".strip()
                vacancy = cls(
                    title=vacancy_data.get('name', ''),
                    url=vacancy_data.get('alternate_url', ''),
                    salary=salary_info,
                    description=description
                )
                vacancies.append(vacancy)
            except Exception as e:
                print(f"Ошибка при создании вакансии: {e}")
                continue

        return vacancies


class FileHandler(ABC):
    """Абстрактный класс для работы с файлами"""

    @abstractmethod
    def add_vacancy(self, vacancy: Vacancy) -> None:
        pass

    @abstractmethod
    def get_vacancies(self, criteria: Dict[str, Any]) -> List[Vacancy]:
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy: Vacancy) -> None:
        pass

    @abstractmethod
    def clear_all(self) -> None:
        pass
