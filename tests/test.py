import unittest
import os
import tempfile
from unittest.mock import patch, Mock


from src.vacanties import Vacancy
from src.api import VacancyAPI, HeadHunterAPI
from src.json import FileHandler, filter_vacancies, get_vacancies_by_salary, sort_vacancies, get_top_vacancies, \
    print_vacancies, JSONSaver


class TestVacancy(unittest.TestCase):

    def setUp(self):
        """Настройка тестовых данных"""
        self.vacancy_with_salary = Vacancy(
            title="Python Developer",
            url="https://hh.ru/vacancy/123",
            salary={'from': 100000, 'to': 150000, 'currency': 'RUR'},
            description="Разработка на Python, опыт от 3 лет"
        )

        self.vacancy_without_salary = Vacancy(
            title="Java Developer",
            url="https://hh.ru/vacancy/456",
            salary=None,
            description="Разработка на Java"
        )

    def test_vacancy_without_salary(self):
        """Тест вакансии без зарплаты"""
        self.assertEqual(self.vacancy_without_salary.salary, "Зарплата не указана")

    def test_salary_comparison(self):
        """Тест сравнения вакансий по зарплате"""
        vacancy_low = Vacancy("Test1", "url1", {'from': 50000}, "desc1")
        vacancy_high = Vacancy("Test2", "url2", {'from': 100000}, "desc2")

        self.assertTrue(vacancy_low < vacancy_high)
        self.assertTrue(vacancy_high > vacancy_low)
        self.assertTrue(vacancy_low <= vacancy_high)
        self.assertTrue(vacancy_high >= vacancy_low)

    def test_get_salary_numeric(self):
        """Тест получения числового значения зарплаты"""
        self.assertEqual(self.vacancy_with_salary.get_salary_numeric(), 100000)
        self.assertEqual(self.vacancy_without_salary.get_salary_numeric(), 0)

    def test_to_dict(self):
        """Тест преобразования в словарь"""
        vacancy_dict = self.vacancy_with_salary.to_dict()
        self.assertEqual(vacancy_dict['title'], "Python Developer")
        self.assertEqual(vacancy_dict['salary'], "100000 - 150000 RUR")


class TestHeadHunterAPI(unittest.TestCase):

    @patch('main.requests.get')
    def test_get_vacancies_success(self, mock_get):
        """Тест успешного получения вакансий"""
        # Мокаем ответ API
        mock_response = Mock()
        mock_response.json.return_value = {
            'items': [
                {
                    'name': 'Python Developer',
                    'alternate_url': 'https://hh.ru/vacancy/123',
                    'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'},
                    'snippet': {'requirement': 'Python', 'responsibility': 'Development'}
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = HeadHunterAPI()
        vacancies = api.get_vacancies("Python")

        self.assertEqual(len(vacancies), 1)
        self.assertEqual(vacancies[0]['name'], 'Python Developer')

    @patch('main.requests.get')
    def test_get_vacancies_failure(self, mock_get):
        """Тест неудачного запроса к API"""
        mock_get.side_effect = Exception("Connection error")

        api = HeadHunterAPI()
        vacancies = api.get_vacancies("Python")

        self.assertEqual(len(vacancies), 0)


class TestJSONSaver(unittest.TestCase):

    def setUp(self):
        """Создание временного файла для тестов"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_filename = self.temp_file.name
        self.temp_file.close()

        self.saver = JSONSaver(self.temp_filename)
        self.test_vacancy = Vacancy(
            title="Test Developer",
            url="https://hh.ru/vacancy/999",
            salary={'from': 50000},
            description="Test description"
        )

    def tearDown(self):
        """Удаление временного файла после тестов"""
        if os.path.exists(self.temp_filename):
            os.unlink(self.temp_filename)

    def test_add_vacancy(self):
        """Тест добавления вакансии"""
        self.saver.add_vacancy(self.test_vacancy)
        vacancies = self.saver.get_vacancies({})

        self.assertEqual(len(vacancies), 1)
        self.assertEqual(vacancies[0].title, "Test Developer")

    def test_delete_vacancy(self):
        """Тест удаления вакансии"""
        self.saver.add_vacancy(self.test_vacancy)
        self.saver.delete_vacancy(self.test_vacancy)
        vacancies = self.saver.get_vacancies({})

        self.assertEqual(len(vacancies), 0)

    def test_get_vacancies_with_keyword(self):
        """Тест поиска вакансий по ключевому слову"""
        self.saver.add_vacancy(self.test_vacancy)

        # Поиск по существующему ключевому слову
        vacancies = self.saver.get_vacancies({'keyword': 'Test'})
        self.assertEqual(len(vacancies), 1)

        # Поиск по несуществующему ключевому слову
        vacancies = self.saver.get_vacancies({'keyword': 'Nonexistent'})
        self.assertEqual(len(vacancies), 0)

    def test_clear_all(self):
        """Тест очистки всех вакансий"""
        self.saver.add_vacancy(self.test_vacancy)
        self.saver.clear_all()
        vacancies = self.saver.get_vacancies({})

        self.assertEqual(len(vacancies), 0)


class TestVacancyFunctions(unittest.TestCase):

    def setUp(self):
        """Создание тестовых вакансий"""
        self.vacancies = [
            Vacancy("Python Senior", "url1", {'from': 200000}, "Senior Python developer"),
            Vacancy("Python Middle", "url2", {'from': 100000}, "Middle Python developer"),
            Vacancy("Python Junior", "url3", {'from': 50000}, "Junior Python developer"),
        ]

    def test_sort_vacancies(self):
        """Тест сортировки вакансий"""
        sorted_vacancies = sorted(self.vacancies, reverse=True)

        self.assertEqual(sorted_vacancies[0].title, "Python Senior")
        self.assertEqual(sorted_vacancies[1].title, "Python Middle")
        self.assertEqual(sorted_vacancies[2].title, "Python Junior")

    def test_filter_vacancies(self):
        """Тест фильтрации вакансий по ключевым словам"""
        filtered = [v for v in self.vacancies if "Senior" in v.title]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].title, "Python Senior")

    def test_get_top_vacancies(self):
        """Тест получения топ N вакансий"""
        top_2 = self.vacancies[:2]
        self.assertEqual(len(top_2), 2)
        self.assertEqual(top_2[0].title, "Python Senior")
        self.assertEqual(top_2[1].title, "Python Middle")
