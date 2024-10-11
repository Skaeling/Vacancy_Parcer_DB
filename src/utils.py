import pandas as pd
import psycopg2
from tabulate import tabulate


def create_database(database_name: str, params: dict) -> None:
    """Создание базы данных и таблиц для сохранения данных о работодателях и вакансиях"""
    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
    cur.execute(f"CREATE DATABASE {database_name}")

    cur.close()
    conn.close()


def represent_results(user_answer: str, db_data: list, keyword: str | None = None) -> None:
    """Возвращает ответ пользователю по полученному номеру запроса"""
    if user_answer == "1":
        msg = f">>> Работодатели и количество открытых вакансий"
        headings = ["Компания", "Количество открытых вакансий"]
        df = pd.DataFrame(db_data, columns=headings)
    elif user_answer == "3":
        msg = f">>> Средняя зарплата по всем вакансиям и работодателям"
        headings = ["Компания", "Средняя заработная плата", "Валюта"]
        df = pd.DataFrame(db_data, columns=headings)
    else:
        headings = ["Компания", "Вакансия", "ЗП от", "ЗП до", "Валюта", "Cсылка на вакансию"]
        df = pd.DataFrame(db_data, columns=headings)
        if user_answer == "2":
            msg = f">>> Доступные для просмотра вакансии"
        elif user_answer == "4":
            msg = f">>> Перечень вакансий с заработной платой выше среднего"
        else:
            msg = f'>>>Результаты поиска по слову: "{keyword}"'
    return print(f"\n{msg}\n{tabulate(df, headers='keys', tablefmt='psql')}")
