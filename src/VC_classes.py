class Vacancy:
    """Класс для обработки и представления пользователю полученной информации из базы данных"""
    def __init__(self, company_name, count_vac=None, vacancy_name=None, salary_min=None, salary_max=None,
                 currency=None, vacancy_url=None, avg_salary=None):
        self.company_name = company_name
        self.count_vac = count_vac
        self.vacancy_name = vacancy_name
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.currency = currency
        self.vacancy_url = vacancy_url
        self.avg_salary = avg_salary

    def __str__(self):
        """Возвращает данные из БД в строковом представлении"""
        msg = ""
        if self.count_vac:
            msg = f'{self.company_name} - Открытых вакансий: {self.count_vac}'
        if self.vacancy_name:
            if self.salary_min == 0:
                self.salary_min = ""
            elif self.salary_max == 0:
                self.salary_max = ""
            else:
                self.salary_max = " до " + str(self.salary_max)
                self.salary_min = "от " + str(self.salary_min)

            msg = f'Компания: {self.company_name}\n' \
                  f'Должность: {self.vacancy_name}\n' \
                  f'Заработная плата: {self.salary_min}{self.salary_max} {self.currency}\n' \
                  f'Ссылка на описание вакансии: {self.vacancy_url}\n\n'
        if self.avg_salary:
            msg = f'В компании "{self.company_name}"\n' \
                  f'Средняя заработная плата составляет: {self.avg_salary} {self.currency}\n\n'

        return msg
