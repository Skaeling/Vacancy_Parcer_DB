from src.API_classes import HHVacancy
from src.config import config
from src.utills import get_emp_data, get_vacancies

def main():
    employees_ids = ['1122462',
                     '1740'
                     ]
    employees_data = get_emp_data(employees_ids)
    vacancy_data = (get_vacancies(employees_data))




# employeers_list = []
    # for i in employeers_id:
    #     n = HHVacancy(i)
    #     employeers_list.append(n)
    # for x in employeers_list:
    #     print(x.get_employees())
    # for i in employeer_1.get_vacancies():
    #     print(i['id'], i['name'], i['area']['name'], i['salary'],
    #           i['snippet'], i['contacts'], i['experience']['name'])

if __name__ == "__main__":
    main()
