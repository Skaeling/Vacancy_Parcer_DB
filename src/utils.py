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


def user_interactive(answer_num: int, word=None):
    if answer_num == 1:
        return f"|Список компаний и количество открытых вакансий|"
    elif answer_num == 5:
        return f'>>>Результаты поиска по слову: "{word}"\n'
