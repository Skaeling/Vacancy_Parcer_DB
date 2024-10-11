from typing import Any

import requests


class HHRequest:
    """Класс для получения информации от HHunter API"""

    def __init__(self, employee_ids: list):
        self.employee_ids = employee_ids
        self.url = "https://api.hh.ru/employers/"

    @staticmethod
    def get_request(url: str, params: dict[Any, Any] | None = None) -> Any:
        """Выполняет запрос к API в соответствии с заданными параметрами"""
        headers = {"User-Agent": "HH-User-Agent"}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            if "salary" in response.text:
                data = response.json()["items"]
            else:
                data = response.json()
            return data
        else:
            print("Error:", response.status_code)

    def get_employers(self) -> list:
        """По employer_id возвращает список с основными данными по работодателю"""
        emp_data = []
        for employer_id in self.employee_ids:
            url = f"{self.url + employer_id}"
            response = self.get_request(url)
            emp_data.append(response)
        return emp_data

    def get_vacancies(self, emp_data: dict) -> list:
        """По employer_id возвращает список открытых вакансий (не более 500 от каждого работодателя),
        с обязательным указанием зп"""
        vac_data = []
        page_count = 1
        if 100 < emp_data["open_vacancies"] < 500:
            page_count = emp_data["open_vacancies"] // 100
        elif emp_data["open_vacancies"] >= 500:
            page_count = 5
        for i in range(page_count):
            params = {
                "text": "",
                "page": i,
                "per_page": 100,
                "employer_id": emp_data["id"],
                "only_with_salary": "true",
            }
            response = self.get_request(emp_data["vacancies_url"], params)
            vac_data.extend(response)
        return vac_data
