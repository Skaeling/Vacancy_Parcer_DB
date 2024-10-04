import psycopg2
from src.VC_classes import Vacancy


class DBManager:
    """Класс для получения информации из базы данных"""
    def __init__(self, database_name: str, params, tb_emp, tb_vac):
        self.conn = psycopg2.connect(dbname=database_name, **params)
        self.cur = self.conn.cursor()
        self.tb_emp = tb_emp
        self.tb_vac = tb_vac

    def get_companies_and_vacancies_count(self):
        """Получает из БД список всех компаний и количества вакансий у каждой компании"""
        emp_vac_count = []
        result = []
        with self.conn:
            self.cur.execute(f'select {self.tb_emp}.company_name, COUNT({self.tb_vac}.vacancy_id) '
                             f'as vacancy_count from {self.tb_emp} '
                             f'JOIN {self.tb_vac} ON {self.tb_emp}.employer_id = {self.tb_vac}.employer_id '
                             f'GROUP BY {self.tb_emp}.company_name')
            data = self.cur.fetchall()
            for v in data:
                emp_vac_count.append({'company_name': v[0], 'count_vac': v[1]})
            for a in emp_vac_count:
                result.append(Vacancy(**a))

            return result

    def get_all_vacancies(self):
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию"""
        all_vacancies = []
        result = []
        with self.conn:
            self.cur.execute(f'select {self.tb_emp}.company_name, vacancy_name, salary_min, salary_max, currency,'
                             f' vacancy_url from {self.tb_vac} '
                             f'JOIN {self.tb_emp} ON {self.tb_vac}.employer_id = {self.tb_emp}.employer_id')
            data = self.cur.fetchall()
            for x in data:
                all_vacancies.append({'company_name': x[0], 'vacancy_name': x[1], 'salary_min': x[2],
                                      'salary_max': x[3], 'currency': x[4], 'vacancy_url': x[5]})
            for a in all_vacancies:
                result.append(Vacancy(**a))
            return result

    def get_avg_salary(self):
        """Получает среднюю зарплату по вакансиям через AVG"""
        avg_salary = []
        result = []
        with self.conn:
            self.cur.execute(f'SELECT company_name, CEILING(AVG(salary_min + salary_max)), currency FROM vacancies '
                             f'JOIN employees ON vacancies.employer_id = employees.employer_id '
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
        high_salary = []
        result = []
        with self.conn:
            self.cur.execute(f'SELECT employees.company_name, vacancy_name, salary_min, salary_max, currency, '
                             f'vacancy_url from vacancies '
                             f'JOIN employees ON vacancies.employer_id = employees.employer_id '
                             f'Where salary_max > (SELECT AVG(salary_max) FROM vacancies) '
                             f'ORDER BY salary_max DESC')
            data = self.cur.fetchall()
            for s in data:
                high_salary.append({'company_name': s[0], 'vacancy_name': s[1], 'salary_min': s[2],
                                    'salary_max': s[3], 'currency': s[4], 'vacancy_url': s[5]})
            for i in high_salary:
                result.append(Vacancy(**i))
            return result

    def get_vacancies_with_keyword(self, keyword):
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова"""
        match_vac = []
        result = []
        with self.conn:
            self.cur.execute(f"SELECT employees.company_name, vacancy_name, salary_min, salary_max, "
                             f"currency, vacancy_url from vacancies "
                             f"JOIN employees ON vacancies.employer_id = employees.employer_id "
                             f"WHERE vacancy_name LIKE '%{keyword}%'")
            data = self.cur.fetchall()
            for t in data:
                match_vac.append({'company_name': t[0], 'vacancy_name': t[1], 'salary_min': t[2],
                                  'salary_max': t[3], 'currency': t[4], 'vacancy_url': t[5]})
            for g in match_vac:
                result.append(Vacancy(**g))
            return result
