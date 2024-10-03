from typing import Any
import requests
from itertools import chain
import psycopg2


def get_emp_data(employees_ids: list) -> list[dict[str, Any]]:
    """Получение данных о работодателях из API hh.ru по employer_id"""
    emp_data = []
    headers = {'User-Agent': 'HH-User-Agent'}
    for employer_id in employees_ids:
        url = f'https://api.hh.ru/employers/{employer_id}'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            employees = response.json()
            emp_data.append(employees)
        else:
            print("Error:", response.status_code)
    return emp_data


def get_vacancies(data: list, page=0) -> list:
    """Получение данных о вакансиях из API hh.ru для ограничения объема данных выбираются первые 100"""
    headers = {'User-Agent': 'HH-User-Agent'}
    vac_data = []
    for i in data:
        params = {'text': '', 'page': page, 'per_page': 10, 'employer_id': i["id"], 'only_with_salary': 'true'}
        response = requests.get(i["vacancies_url"], headers=headers, params=params)
        if response.status_code == 200:
            vacancies = response.json()['items']
            # vac_data.append({'employer': i["id"], 'vacancy': vacancies})
            vac_data.append(vacancies)
        else:
            print("Error:", response.status_code)
    return list(chain.from_iterable(vac_data))


def get_vacancies_over100(data):
    response = []
    for page in range(20):
        values = get_vacancies(data, page)
        response.extend(values)
    return response

def create_database(database_name: str, params: dict) -> None:
    """Создание базы данных и таблиц для сохранения данных о работодателях и вакансиях"""
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f'DROP DATABASE IF EXISTS {database_name}')
    cur.execute(f'CREATE DATABASE {database_name}')

    cur.close()
    conn.close()

    with psycopg2.connect(dbname=database_name, **params) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """CREATE TABLE employees (
                employer_id INT PRIMARY KEY,
                company_name VARCHAR(100) NOT NULL,
                open_vacancies INT NOT NULL,
                location VARCHAR(50),
                employer_url TEXT
                )
                """)

        with conn.cursor() as cur:
            cur.execute(
                """CREATE TABLE vacancies (
                vacancy_id INT PRIMARY KEY,
                vacancy_name VARCHAR(100) NOT NULL,
                employer_id INT NOT NULL,
                salary_min INT DEFAULT 0,
                salary_max INT DEFAULT 0,
                currency CHAR(10),
                vacancy_url TEXT,
                experience TEXT,
                type VARCHAR(100),
                FOREIGN KEY (employer_id) REFERENCES employees(employer_id)
                )
                """)
    conn.close()


def save_data_to_database(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """Сохранение данных о работодателях в базу данных"""
    with psycopg2.connect(dbname=database_name, **params) as conn:
        with conn.cursor() as cur:
            for emp in data:
                cur.execute("""
                        INSERT INTO employees (employer_id, company_name, open_vacancies, location, employer_url)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING employer_id
                        """,
                            (emp['id'], emp['name'], emp['open_vacancies'], emp['area']['name'],
                             emp['site_url'])
                            )
                employer_id = cur.fetchone()[0]  # (1, )

    conn.close()


def save_vacancy_to_database(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """Сохранение данных о вакансиях в базу данных"""
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
                # employer_id = cur.fetchone()[0]  # (1, )

    conn.close()

