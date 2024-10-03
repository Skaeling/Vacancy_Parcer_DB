import psycopg2


class DBManager:

    def __init__(self, database_name: str, params):
        self.conn = psycopg2.connect(dbname=database_name, **params)
        self.cur = self.conn.cursor()

    def get_companies_and_vacancies_count(self, employees: str, vacancies: str):
        """Получает из БД список всех компаний и количества вакансий у каждой компании"""
        emp_vac_count = []
        with self.conn:
            self.cur.execute(f'select {employees}.company_name, COUNT({vacancies}.vacancy_id) '
                             f'as vacancy_count from {employees} '
                             f'JOIN {vacancies} ON {employees}.employer_id = {vacancies}.employer_id '
                             f'GROUP BY {employees}.company_name')
            data = self.cur.fetchall()
            for v in data:
                emp_vac_count.append({'company_name': v[0], 'count_vac': v[1]})
            return emp_vac_count

    def get_all_vacancies(self):
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию"""
        all_vacancies = []
        with self.conn:
            self.cur.execute(f'select employees.company_name, vacancy_name, salary_min, salary_max, vacancy_url '
                             f'from vacancies JOIN employees ON vacancies.employer_id = employees.employer_id')
            data = self.cur.fetchall()
            for x in data:
                all_vacancies.append({'company_name': x[0], 'vacancy_name': x[1], 'salary_min': x[2],
                                      'salary_max': x[3], 'vacancy_url': x[4]})
            return all_vacancies

    def get_avg_salary(self):
        """Получает среднюю зарплату по вакансиям через AVG"""
        with self.conn:
            self.cur.execute(f'SELECT company_name, CEILING(AVG(salary_min)) as avg_salary_min, '
                             f'CEILING(AVG(salary_max)) as avg_salary_max from vacancies '
                             f'JOIN employees ON vacancies.employer_id = employees.employer_id '
                             f'Where salary_max <> 0  and salary_min <> 0 '
                             f'GROUP BY company_name')
            data = self.cur.fetchall()
            return data

    def get_vacancies_with_higher_salary(self):
        """Выводи список вакансий, у которых зарплата выше средней по всем вакансиям"""
        with self.conn:
            self.cur.execute(f'SELECT * from vacancies '
                             f'Where salary_max > (SELECT AVG(salary_max) FROM vacancies)')
            data = self.cur.fetchall()
            return data

    def get_vacancies_with_keyword(self, keyword):
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова"""
        with self.conn:
            self.cur.execute(f"select * from vacancies "
                             f"WHERE vacancy_name LIKE '%{keyword}%'")
            data = self.cur.fetchall()
            return data
