import psycopg2
from src.VC_classes import Vacancy


class DBManager:
    """Класс для работы с базами данных employers и vacancies"""

    def __init__(self, database_name: str, params, emp, vac):
        self.conn = psycopg2.connect(dbname=database_name, **params)
        self.cur = self.conn.cursor()
        self.emp = emp
        self.vac = vac
        self._create_tables("src/create_tab.sql")

    def _create_tables(self, sql_path):
        with self.conn:
            with open(sql_path, 'r') as file:
                self.cur.execute(file.read())

    def save_emp_to_database(self):
        """Сохранение данных о работодателях в базу данных hh"""
        with self.conn:
            for e in self.emp:
                self.cur.execute("""
                            INSERT INTO employers (employer_id, company_name, open_vacancies, location, employer_url)
                            VALUES (%s, %s, %s, %s, %s)
                            RETURNING employer_id
                            """,
                                 (e['id'], e['name'], e['open_vacancies'], e['area']['name'],
                                  e['site_url'])
                                 )

    def save_vacancy_to_database(self):
        """Сохранение данных о вакансиях в базу данных hh"""
        with self.conn:
            for vac in self.vac:
                if vac['salary']['from'] is None:
                    salary_min = 0
                    salary_max = vac['salary']['to']
                elif vac['salary']['to'] is None:
                    salary_max = 0
                    salary_min = vac['salary']['from']
                else:
                    salary_min = vac['salary']['from']
                    salary_max = vac['salary']['to']
                self.cur.execute("""
                            INSERT INTO vacancies (vacancy_id, vacancy_name, employer_id, salary_min, salary_max, currency, 
                            vacancy_url, experience, type)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                                 (vac['id'], vac['name'], vac['employer']['id'], salary_min, salary_max,
                                  vac['salary']['currency'], vac['alternate_url'], vac['experience']['name'],
                                  vac['type']['name'])
                                 )

    def get_companies_and_vacancies_count(self):
        """Получает из БД список всех компаний и количества вакансий у каждой компании"""
        emp_vac_count = []
        result = []
        with self.conn:
            self.cur.execute(f'select employers.company_name, COUNT(vacancies.vacancy_id) '
                             f'as vacancy_count from employers '
                             f'JOIN vacancies ON employers.employer_id = vacancies.employer_id '
                             f'GROUP BY employers.company_name')
            data = self.cur.fetchall()
            for v in data:
                emp_vac_count.append({'company_name': v[0], 'count_vac': v[1]})
            for a in emp_vac_count:
                result.append(Vacancy(**a))

            return result

    def get_all_vacancies(self):
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию"""

        with self.conn:
            self.cur.execute(f'select employers.company_name, vacancy_name, salary_min, salary_max, currency,'
                             f' vacancy_url from vacancies '
                             f'JOIN employers ON vacancies.employer_id = employers.employer_id')
            data = self.cur.fetchall()
            return self.prepare_user_data(data)

    def get_avg_salary(self):
        """Получает среднюю зарплату по вакансиям через AVG"""
        avg_salary = []
        result = []
        with self.conn:
            self.cur.execute(f'SELECT company_name, CEILING(AVG(salary_min + salary_max)), currency FROM vacancies '
                             f'JOIN employers ON vacancies.employer_id = employers.employer_id '
                             f'Where salary_max <> 0 and salary_min <> 0 '
                             f'GROUP BY company_name, currency')
            data = self.cur.fetchall()
            for n in data:
                avg_salary.append({'company_name': n[0], 'avg_salary': n[1], 'currency': n[2]})
            for f in avg_salary:
                result.append(Vacancy(**f))

            return result

    def get_vacancies_with_higher_salary(self):
        """Выводит список вакансий, у которых зарплата выше средней по всем вакансиям"""

        with self.conn:
            self.cur.execute(f'SELECT employers.company_name, vacancy_name, salary_min, salary_max, currency, '
                             f'vacancy_url from vacancies '
                             f'JOIN employers ON vacancies.employer_id = employers.employer_id '
                             f'Where salary_max > (SELECT AVG(salary_max) FROM vacancies) '
                             f'ORDER BY salary_max DESC')
            data = self.cur.fetchall()
            return self.prepare_user_data(data)

    def get_vacancies_with_keyword(self, keyword: str) -> list:
        """Получает список всех вакансий, в названии которых содержится переданное в метод слово"""

        with self.conn:
            self.cur.execute(f"SELECT employers.company_name, vacancy_name, salary_min, salary_max, "
                             f"currency, vacancy_url from vacancies "
                             f"JOIN employers ON vacancies.employer_id = employers.employer_id "
                             f"WHERE vacancy_name LIKE '%{keyword}%'")
            data = self.cur.fetchall()
            return self.prepare_user_data(data)

    @staticmethod
    def prepare_user_data(data) -> list:
        """Обрабатывает кортеж полученных строк из базы данных, преобразует его в экземпляр класса Vacancy"""
        data_dict = []
        data_list = []
        for s in data:
            data_dict.append({'company_name': s[0], 'vacancy_name': s[1], 'salary_min': s[2],
                              'salary_max': s[3], 'currency': s[4], 'vacancy_url': s[5]})
        for i in data_dict:
            data_list.append(Vacancy(**i))
        return data_list
