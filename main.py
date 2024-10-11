from src.API_classes import HHRequest
from src.config import config
from src.DB_classes import DBCreator, DBManager
from src.utils import create_database, represent_results


def main():
    print(
        "\nПриветствуем вас в подборе вакансий! \n\n"
        "Доступные действия: \n"
        "1. Получить перечень 10 компаний-работодателей и их открытых вакансий\n"
        "2. Просмотреть все доступные вакансии\n"
        "3. Узнать среднюю зарплату по открытым вакансиям\n"
        "4. Просмотреть список всех вакансий с заработной платой выше среднего\n"
        "5. Подобрать вакансии по ключевому слову\n"
        "6. Завершить подбор\n"
    )
    user_answer = input("Введите номер опции, чтобы отправить запрос: ")

    if user_answer not in "123456":
        print("Нет такой категории, пожалуйста, выберите другую")
        main()
    elif user_answer == "6":
        quit()
    else:
        # Отправка запроса к API
        employers_ids = [
            "5569859",
            "6093775",
            "64174",
            "4934",
            "2324020",
            "3776",
            "3331449",
            "3769",
            "370421",
            "999442",
        ]
        api_hh = HHRequest(employers_ids)
        employers_data = api_hh.get_employers()
        vacancies_data = []
        [vacancies_data.extend(api_hh.get_vacancies(v)) for v in employers_data]

        #  Создание БД для хранения полученной из API информации
        params = config()
        create_database("hh", params)

        #  Создание таблиц и загрузка в них данных
        db = DBCreator("hh", params, employers_data, vacancies_data)

        #  Получение данных из таблиц и презентация пользователю
        hh = DBManager("hh", params, employers_data, vacancies_data)

        if user_answer == "5":
            user_keyword = input("Введите ключевое слово для поиска вакансии ")
            search_vacancy = hh.get_vacancies_with_keyword(user_keyword)
            if not search_vacancy:
                print("\nК сожалению, ничего не найдено")
                user_choice = input("Начать новый поиск? (да/нет) ").lower()
                if user_choice == "да":
                    db.close_db()
                    hh.close_db()
                    main()
                else:
                    quit()
            else:
                represent_results(user_answer, search_vacancy, user_keyword)
        else:
            hh_methods = {
                "1": hh.get_companies_and_vacancies_count(),
                "2": hh.get_all_vacancies(),
                "3": hh.get_avg_salary(),
                "4": hh.get_vacancies_with_higher_salary(),
            }
            represent_results(user_answer, hh_methods.get(user_answer))
            new_search = input("Направить новый запрос? (да/нет) ").lower()
            if new_search == "да":
                db.close_db()
                hh.close_db()
                main()
            else:
                quit()


if __name__ == "__main__":
    main()
