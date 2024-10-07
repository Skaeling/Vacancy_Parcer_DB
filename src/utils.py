from typing import Any
import psycopg2


def create_database(database_name: str, params: dict) -> None:
    """Создание базы данных и таблиц для сохранения данных о работодателях и вакансиях"""
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f'DROP DATABASE IF EXISTS {database_name}')
    cur.execute(f'CREATE DATABASE {database_name}')

    cur.close()
    conn.close()


def create_tables(database_name: str, params: dict, sql_path):
    with psycopg2.connect(dbname=database_name, **params) as conn:
        with conn.cursor() as cur:
            with open(sql_path, 'r') as file:
                cur.execute(file.read())

    conn.close()


def save_emp_to_database(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """Сохранение данных о работодателях в базу данных hh"""
    with psycopg2.connect(dbname=database_name, **params) as conn:
        with conn.cursor() as cur:
            for emp in data:
                cur.execute("""
                        INSERT INTO employers (employer_id, company_name, open_vacancies, location, employer_url)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING employer_id
                        """,
                            (emp['id'], emp['name'], emp['open_vacancies'], emp['area']['name'],
                             emp['site_url'])
                            )

    conn.close()


def save_vacancy_to_database(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """Сохранение данных о вакансиях в базу данных hh"""
    with psycopg2.connect(dbname=database_name, **params) as conn:
        with conn.cursor() as cur:
            for vac in data:
                if vac['salary']['from'] is None:
                    salary_min = 0
                    salary_max = vac['salary']['to']
                elif vac['salary']['to'] is None:
                    salary_max = 0
                    salary_min = vac['salary']['from']
                else:
                    salary_min = vac['salary']['from']
                    salary_max = vac['salary']['to']
                cur.execute("""
                        INSERT INTO vacancies (vacancy_id, vacancy_name, employer_id, salary_min, salary_max, currency, 
                        vacancy_url, experience, type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                            (vac['id'], vac['name'], vac['employer']['id'], salary_min, salary_max,
                             vac['salary']['currency'], vac['alternate_url'], vac['experience']['name'],
                             vac['type']['name'])
                            )

    conn.close()


def user_interactive(answer_num: int, word=None):
    if answer_num == 1:
        return f"|Список компаний и количество открытых вакансий|"
    elif answer_num == 5:
        return f'>>>Результаты поиска по слову: "{word}"\n'
