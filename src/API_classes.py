from abc import ABC, abstractmethod
from itertools import chain

import requests
from typing import Any

VACANCY_COUNT = 100
PAGE_COUNT = 10


class API(ABC):
    @abstractmethod
    def get_request(self, url, params):
        pass

    @abstractmethod
    def get_vacancies(self, keyword):
        pass


class HHVacancy(API):
    """Класс для взаимодействия с HHunter API"""
    def __init__(self, employee_ids: list):
        self.employee_ids = employee_ids
        self.url = 'https://api.hh.ru/employers/'

    def get_request(self, url, params=None) -> list[dict[str, Any]]:
        headers = {'User-Agent': 'HH-User-Agent'}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            if 'salary' in response.text:
                data = response.json()['items']
            else:
                data = response.json()
            return data

        else:
            print("Error:", response.status_code)

    def get_employers(self) -> list:
        """По employer_id возвращает список с основными данными по работодателю"""
        emp_data = []
        for employer_id in self.employee_ids:
            url = f'{self.url+employer_id}'
            response = self.get_request(url)
            emp_data.append(response)
        return emp_data

    def get_vacancies(self, emp_data: list) -> list:
        """По employer_id возвращает список вакансий заданных работодателей"""
        vac_data = []
        for i in emp_data:
            params = {'text': '', 'page': 0, 'per_page': 10, 'employer_id': i["id"], 'only_with_salary': 'true'}
            response = self.get_request(i["vacancies_url"], params)
            vac_data.append(response)
        return list(chain.from_iterable(vac_data))
