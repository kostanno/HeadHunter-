from src.vacanties import Vacancy
from src.api import HeadHunterAPI
from src.json import  filter_vacancies, get_vacancies_by_salary, sort_vacancies, get_top_vacancies, \
    print_vacancies, JSONSaver


def user_interaction():
    """Функция для взаимодействия с пользователем"""
    print("Добро пожаловать в программу поиска вакансий!")
    print("=" * 50)

    hh_api = HeadHunterAPI()
    json_saver = JSONSaver()

    while True:
        print("\nМеню:")
        print("1. Поиск вакансий на hh.ru")
        print("2. Показать сохраненные вакансии")
        print("3. Фильтровать сохраненные вакансии")
        print("4. Удалить вакансию")
        print("5. Очистить все вакансии")
        print("6. Выход")
        choice = input("\nВыберите действие (1-6): ").strip()
        if choice == '1':
            search_query = input("Введите поисковый запрос: ").strip()
            if not search_query:
                print("Поисковый запрос не может быть пустым!")
                continue
            print("Ищем вакансии...")
            vacancies_data = hh_api.get_vacancies(search_query)
            if not vacancies_data:
                print("Вакансии не найдены.")
                continue
            vacancies_list = Vacancy.cast_to_object_list(vacancies_data)
            print(f"Найдено {len(vacancies_list)} вакансий.")
            for vacancy in vacancies_list:
                json_saver.add_vacancy(vacancy)
            try:
                top_n = int(input("Введите количество вакансий для вывода в топ N: "))
            except ValueError:
                top_n = 10
            filter_words = input("Введите ключевые слова для фильтрации вакансий (через пробел): ").split()
            salary_range = input("Введите диапазон зарплат (например: 100000-150000): ").strip()
            filtered_vacancies = filter_vacancies(vacancies_list, filter_words)
            ranged_vacancies = get_vacancies_by_salary(filtered_vacancies, salary_range)
            sorted_vacancies = sort_vacancies(ranged_vacancies)
            top_vacancies = get_top_vacancies(sorted_vacancies, top_n)
            print(f"\nРезультаты поиска (показано {len(top_vacancies)} вакансий):")
            print_vacancies(top_vacancies)
        elif choice == '2':
            all_vacancies = json_saver.get_vacancies({})
            if not all_vacancies:
                print("Нет сохраненных вакансий.")
            else:
                print(f"\nВсего сохранено {len(all_vacancies)} вакансий:")
                print_vacancies(all_vacancies)

        elif choice == '3':
            print("\nФильтрация вакансий:")
            print("1. По ключевому слову")
            print("2. По минимальной зарплате")
            print("3. Только с указанной зарплатой")
            print("4. Только без указанной зарплаты")
            filter_choice = input("Выберите тип фильтра (1-4): ").strip()
            if filter_choice == '1':
                keyword = input("Введите ключевое слово: ").strip()
                filtered = json_saver.get_vacancies({'keyword': keyword})
            elif filter_choice == '2':
                try:
                    min_salary = int(input("Введите минимальную зарплату: "))
                    filtered = json_saver.get_vacancies({'min_salary': min_salary})
                except ValueError:
                    print("Неверный формат зарплаты!")
                    continue
            elif filter_choice == '3':
                filtered = json_saver.get_vacancies({'salary': 'with_salary'})
            elif filter_choice == '4':
                filtered = json_saver.get_vacancies({'salary': 'without_salary'})
            else:
                print("Неверный выбор!")
                continue
            if filtered:
                print(f"\nНайдено {len(filtered)} вакансий:")
                print_vacancies(filtered)
            else:
                print("Вакансии не найдены.")
        elif choice == '4':
            all_vacancies = json_saver.get_vacancies({})
            if not all_vacancies:
                print("Нет сохраненных вакансий для удаления.")
                continue
            print("\nСписок вакансий:")
            for i, vacancy in enumerate(all_vacancies, 1):
                print(f"{i}. {vacancy.title} - {vacancy.salary}")
            try:
                vacancy_num = int(input("\nВведите номер вакансии для удаления: "))
                if 1 <= vacancy_num <= len(all_vacancies):
                    vacancy_to_delete = all_vacancies[vacancy_num - 1]
                    json_saver.delete_vacancy(vacancy_to_delete)
                    print("Вакансия удалена!")
                else:
                    print("Неверный номер вакансии!")
            except ValueError:
                print("Неверный формат номера!")

        elif choice == '5':
            confirm = input("Вы уверены, что хотите удалить все вакансии? (ДА/НЕТ): ").strip().lower()
            if confirm == 'ДА':
                json_saver.clear_all()
                print("Все вакансии удалены!")
        elif choice == '6':
            print("До свидания!")
            break
        else:
            print("Неверный выбор! Попробуйте снова.")


if __name__ == "__main__":
    user_interaction()
