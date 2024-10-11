from typing import Any

import psycopg2


class DBCreator:
    """Класс для создания таблиц и сохранения в них данных полученных от API"""

    def __init__(self, database_name: str, params: dict, emp: list, vac: list):
        self._conn = psycopg2.connect(dbname=database_name, **params)
        self._cur = self._conn.cursor()
        self.emp = emp
        self.vac = vac
        self.__create_tables("src/create_tabs.sql")
        self.__save_emp_to_database()
        self.__save_vacancy_to_database()

    def __create_tables(self, sql_path: str) -> None:
        """Создает таблицы employers и vacancies по sql-скрипту"""
        with self._conn:
            with open(sql_path, "r") as file:
                self._cur.execute(file.read())

    def close_db(self) -> None:
        """Закрывает курсор и соединение с БД"""
        self._cur.close()
        self._conn.close()

    def __save_emp_to_database(self) -> None:
        """Сохраняет данные о работодателях в таблицу employers"""
        with self._conn:
            for e in self.emp:
                self._cur.execute(
                    """INSERT INTO employers (employer_id, company_name, location, employer_url, description)
                            VALUES (%s, %s, %s, %s, %s)
                            RETURNING employer_id
                            """,
                    (e["id"], e["name"].title(), e["area"]["name"], e["site_url"], e["description"]),
                )

    def __save_vacancy_to_database(self) -> None:
        """Сохраняет данные о вакансиях в таблицу vacancies"""
        with self._conn:
            for vac in self.vac:
                if vac["salary"]["from"] is None:
                    salary_min = 0
                    salary_max = vac["salary"]["to"]
                elif vac["salary"]["to"] is None:
                    salary_max = 0
                    salary_min = vac["salary"]["from"]
                else:
                    salary_min = vac["salary"]["from"]
                    salary_max = vac["salary"]["to"]
                self._cur.execute(
                    """INSERT INTO vacancies (vacancy_id, vacancy_name, employer_id, salary_min, salary_max, 
                            currency, vacancy_url, experience, type)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                    (
                        vac["id"],
                        vac["name"],
                        vac["employer"]["id"],
                        salary_min,
                        salary_max,
                        vac["salary"]["currency"],
                        vac["alternate_url"],
                        vac["experience"]["name"],
                        vac["type"]["name"],
                    ),
                )


class DBManager(DBCreator):
    """Класс для получения данных из БД hh"""

    def get_companies_and_vacancies_count(self) -> Any:
        """Получает из БД список всех компаний и количества вакансий у каждой компании"""
        with self._conn:
            self._cur.execute(
                f"select employers.company_name, COUNT(vacancies.vacancy_id) "
                f"as vacancy_count from employers "
                f"JOIN vacancies ON employers.employer_id = vacancies.employer_id "
                f"GROUP BY employers.company_name "
                f"ORDER BY employers.company_name"
            )
            emp_data = self._cur.fetchall()
            return emp_data

    def get_all_vacancies(self) -> Any:
        """Получает из БД список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию"""

        with self._conn:
            self._cur.execute(
                f"select employers.company_name, vacancy_name as vacancy, salary_min, "
                f"salary_max, currency, vacancy_url from vacancies "
                f"JOIN employers ON vacancies.employer_id = employers.employer_id "
                f"ORDER BY employers.company_name"
            )
            vac_data = self._cur.fetchall()
            return vac_data

    def get_avg_salary(self) -> Any:
        """Получает из БД среднюю зарплату по вакансиям"""
        with self._conn:
            self._cur.execute(
                f"SELECT company_name, CEILING(AVG(salary_min + salary_max)), currency FROM vacancies "
                f"JOIN employers ON vacancies.employer_id = employers.employer_id "
                f"Where salary_max <> 0 and salary_min <> 0 "
                f"GROUP BY company_name, currency "
                f"ORDER BY employers.company_name"
            )
            avg_salary = self._cur.fetchall()
            return avg_salary

    def get_vacancies_with_higher_salary(self) -> Any:
        """Получает из БД список вакансий, у которых зарплата выше средней по всем вакансиям"""
        with self._conn:
            self._cur.execute(
                f"SELECT employers.company_name, vacancy_name, salary_min, salary_max, currency, "
                f"vacancy_url from vacancies "
                f"JOIN employers ON vacancies.employer_id = employers.employer_id "
                f"Where salary_max > (SELECT AVG(salary_max) FROM vacancies) "
                f"ORDER BY salary_max DESC"
            )
            high_sal_vac = self._cur.fetchall()
            return high_sal_vac

    def get_vacancies_with_keyword(self, keyword: str) -> Any:
        """Получает из БД список всех вакансий, в названии которых содержится переданное в метод слово"""

        with self._conn:
            self._cur.execute(
                f"SELECT employers.company_name, vacancy_name, salary_min, salary_max, "
                f"currency, vacancy_url from vacancies "
                f"JOIN employers ON vacancies.employer_id = employers.employer_id "
                f"WHERE vacancy_name LIKE '%{keyword.title()}%' or vacancy_name LIKE '%{keyword.lower()}%'"
            )
            keyword_vacancy = self._cur.fetchall()
            return keyword_vacancy
