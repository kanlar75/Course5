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


class DBManager:
    """ Класс DBManager, который подключается к БД Postgres. """

    def __init__(self, pass_, name='vac'):
        self.conn = None
        self.dbname = name
        self.pass_ = pass_
        self.conn_new = psycopg2.connect(
            user='postgres',
            password=self.pass_,
            host='localhost',
            port='5432')

    def set_conn(self):
        """ Устанавливает соединение с базой данных. """

        self.conn = psycopg2.connect(
            database=self.dbname,
            user='postgres',
            password=self.pass_,
            host='localhost',
            port='5432'
        )
        return self.conn

    def creat_db(self):
        """ Создание базы данных. """

        self.conn_new.autocommit = True
        cur = self.conn_new.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname='{dbname}'".
                    format(dbname=self.dbname))
        if cur.fetchone() is None:
            cur.execute(f' CREATE DATABASE {self.dbname}')
        cur.close()
        self.conn_new.close()

    def creat_table_employers_tab(self):
        """ Создание таблицы по работодателям. """

        self.set_conn()
        self.conn.autocommit = True
        with self.conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS employers_tab(
            employer_id int PRIMARY KEY,
            employer_name varchar(255),
            employer_url varchar(255),
            open_vac int)
            '''
                        )
        self.conn.close()

    def creat_table_vacancies_tab(self):
        """ Создание таблицы по вакансиям. """

        self.set_conn()
        self.conn.autocommit = True
        with self.conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS vacancies_tab(
            vacancy_id int PRIMARY KEY,
            employer_id int REFERENCES employers_tab(employer_id) 
            on delete restrict
            on update restrict,
            title varchar(255),
            url varchar(255),
            salary_from int,
            salary_to int,
            currency varchar(15),
            description text,
            town varchar(255),
            education text,
            experience varchar(255),
            date_pub date);
            ''')
        self.conn.close()

    def instance_emp_from_lst(self, emp_list):
        """ Заполняем таблицу employers_tab из списка """

        self.set_conn()
        self.conn.autocommit = True
        with self.conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE employers_tab CASCADE")
            for emp in emp_list:
                cur.execute(
                    "INSERT INTO employers_tab VALUES (%s, %s, %s, %s)",
                    (emp['employer_id'], emp['employer_name'],
                     emp['url'], emp['open_vac']))
        self.conn.close()

    def instance_vac_from_lst(self, vac_list):
        """ Заполняем таблицу vacancies_tab из списка. """

        self.set_conn()
        self.conn.autocommit = True
        with self.conn.cursor() as cur:
            for vac in vac_list:
                cur.execute("INSERT INTO vacancies_tab VALUES (%s, %s, "
                            "%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
                            (vac['vacancy_id'], vac['employer_id'],
                             vac["title"],
                             vac['url'], vac['salary_from'],
                             vac['salary_to'], vac['currency'],
                             vac['description'], vac[
                                 'town'], vac['education'],
                             vac['experience'], vac['date_pub'],
                             ))
        self.conn.close()



