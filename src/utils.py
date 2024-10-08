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


def user_interactive(user_answer: str, db_data: list, keyword=None):
    """Возвращает ответ пользователю по полученному номеру вопроса"""
    if user_answer == '1':
        msg = f"|Работодатели и количество открытых вакансий|"
    elif user_answer == '2':
        msg = f'|Доступные для просмотра вакансии|'
    elif user_answer == '3':
        msg = f'|Средняя зарплата по всем вакансиям и работодателям|'
    elif user_answer == '4':
        msg = f'|Перечень вакансий с заработной платой выше среднего|'
    else:
        if not db_data:
            msg = "К сожалению, ничего не найдено"
        else:
            msg = f'>>>Результаты поиска по слову: "{keyword}"\n'
    return print(msg), [print(d) for d in db_data]
