from src.config import config
from src.utils import create_database, user_interactive
from src.DB_classes import DBManager
from src.API_classes import HHVacancy


def main():
    #  Получение информации по работодателям
    #  и предлагаемым ими вакансиям из списка 10 работодателей

    employers_ids = ['1122462',
                     '1740'
                     ]
    emp_clas = HHVacancy(employers_ids)
    employers_data = emp_clas.get_employers()
    vacancies_data = emp_clas.get_vacancies(employers_data)
    # print(ids)
    # print(vacs)

    #  Создание БД для хранения полученной из API информации
    params = config()
    create_database('hh', params)

    #  Создание таблиц и загрузка в них данных
    db = DBManager('hh', params, employers_data, vacancies_data)
    db.save_emp_to_database()
    db.save_vacancy_to_database()

    print('\nПриветствуем вас в парсере вакансий! \n'
          'Введите номер опции чтобы отправить запрос:\n')
    print('1. Получить перечень 10 доступных компаний и их открытых вакансий\n'
          '2. Просмотреть все доступные вакансии\n'
          '3. Узнать среднюю зарплату доступных вакансий\n'
          '4. Узнать список всех вакансий с заработной платы выше среднего\n'
          '5. Подобрать вакансии по ключевому слову\n'
          '6. Завершить подбор\n')
    user_answer = input()
    db_methods = {'1': db.get_companies_and_vacancies_count(), '2': db.get_all_vacancies(),
                  '3': db.get_avg_salary(), '4': db.get_vacancies_with_higher_salary()}
    if user_answer not in '123456':
        print("Нет такой категории")
        main()
    elif user_answer == '6':
        quit()
    elif user_answer == '5':
        user_keyword = input('Введите слово для поиска вакансии ').title()
        search_vacancy = db.get_vacancies_with_keyword(user_keyword)
        user_interactive(user_answer, search_vacancy, user_keyword)
    else:
        user_interactive(user_answer, db_methods.get(user_answer))


if __name__ == "__main__":
    main()
