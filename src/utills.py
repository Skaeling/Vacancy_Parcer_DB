from typing import Any
import requests
from itertools import chain


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


def get_vacancies(data: list) -> list:
    """Получение данных о вакансиях из API hh.ru"""
    headers = {'User-Agent': 'HH-User-Agent'}
    vac_data = []
    for i in data:
        params = {'text': '', 'page': 0, 'per_page': 100, 'employer_id': i["id"]}
        response = requests.get(i["vacancies_url"], headers=headers, params=params)
        if response.status_code == 200:
            vacancies = response.json()['items']
            vac_data.append({'employeer': i["id"], 'vacancy': vacancies})
        else:
            print("Error:", response.status_code)
    # res = list(chain.from_iterable(vac_data))
    return vac_data

    # ['id'], employees['name'], employees['type'], employees['open_vacancies'],
    # employees['site_url'], employees['area']['name'],
    # employees['industries'][0]['name']]
#
# data.append({
#             'channel': channel_data['items'][0],
#             'videos': videos_data
#         })


def create_database(database_name: str, params: dict) -> None:
    """Создание базы данных и таблиц для сохранения данных о работодателях и вакансиях"""
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()


def save_data_to_database(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """Сохранение данных о работодателях и вакансиях в базу данных"""
    pass
