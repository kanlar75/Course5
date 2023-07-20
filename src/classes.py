import requests
import fake_useragent
import psycopg2
from src.variables import vacancies_on_page, employers_id, pages


class HeadHunterAPI:
    """ Класс для работы с вакансиями с HeadHunter """

    headers = {'user-agent': fake_useragent.UserAgent().random}
    params = {'per_page': vacancies_on_page, 'employer_id':
        employers_id.values(), 'archive': False}

    def get_employers(self):
        """
        Получение списка работодателей. Выходные данные в формате списка
        словарей Python - работа с requests и JSON. (id работодателей в
        словаре employers_id в файле variables.py).
        """

        self.params["only_with_vacancies"] = True
        emp_list_hh = []
        for id_ in employers_id.values():
            response = requests.get(f"https://api.hh.ru/employers/"
                                    f"{id_}", params=self.params,
                                    headers=self.headers).json()

            employers_dic = {'employer_id': response['id'], 'employer_name':
                             response['name'],
                             'url': response['alternate_url'],
                             'open_vac': response['open_vacancies']}
            emp_list_hh.append(employers_dic)
        return emp_list_hh

    def get_vacancies(self):
        """
        Получение списка вакансий по интересующим работодателям.
        (id работодателей в словаре employers_id в файле variables.py. Выходные
        данные в формате списка словарей Python - работа с requests и JSON).
        """

        vac_list_hh = []
        for page in range(pages):
            self.params['page'] = page
            data_hh = requests.get(f'https://api.hh.ru/vacancies?',
                                   params=self.params,
                                   headers=self.headers).json()
            for i in range(vacancies_on_page):
                vac_dict_hh = {'vacancy_id': data_hh['items'][i]['id'],
                               'title': data_hh['items'][i]['name'],
                               'url': data_hh['items'][i]['alternate_url'],
                               'employer_id': data_hh['items'][i][
                                   'employer']['id'],
                               'employer_name': data_hh['items'][i][
                                   'employer']['name']}
                if data_hh['items'][i]['salary'] is not None:
                    vac_dict_hh['salary_from'] = data_hh['items'][i]['salary'][
                        'from']
                    vac_dict_hh['salary_to'] = data_hh['items'][i]['salary'][
                        'to']
                    vac_dict_hh['currency'] = data_hh['items'][i]['salary'][
                        'currency']
                else:
                    vac_dict_hh['salary_from'] = 0
                    vac_dict_hh['salary_to'] = 0
                    vac_dict_hh['currency'] = 'не указано'
                vac_dict_hh['description'] = data_hh['items'][i]['snippet'][
                    'responsibility']
                vac_dict_hh['town'] = data_hh['items'][i]['area']['name']
                vac_dict_hh['education'] = data_hh['items'][i]['snippet'][
                    'requirement']
                vac_dict_hh['experience'] = data_hh['items'][i]['experience'][
                    'name']
                vac_dict_hh['date_pub'] = data_hh['items'][i]['published_at']
                vac_list_hh.append(vac_dict_hh)
        return vac_list_hh
