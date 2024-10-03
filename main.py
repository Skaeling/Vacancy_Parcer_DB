from src.config import config
from src.utills import get_emp_data, get_vacancies, create_database, save_data_to_database, save_vacancy_to_database


def main():
    #  Получение информации по работодателям и предлагаемым ими вакансиям

    employees_ids = ['1122462',
                     '1740'
                     ]
    employees_data = get_emp_data(employees_ids)
    vacancy_data = (get_vacancies(employees_data))


    #  Создание БД для хранения полученной информации
    params = config()
    create_database('hh', params)
    save_data_to_database(employees_data, 'hh', params)
    save_vacancy_to_database(vacancy_data, 'hh', params)



if __name__ == "__main__":
    main()
