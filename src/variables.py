import fake_useragent


vacancies_on_page = 100
pages = 20

employers_id = {
        "Сбербанк России": 3529,
        "Webtronics": 5843588,
        "ООО СФЕРА": 4402893,
        "Алроса": 92288,
        "Convergent": 57862,
        "Mindbox": 205152,
        "Звук": 1829949,
        "Точка": 2324020,
        "ВТБ": 4181,
        "B.ART": 9352347
    }

headers = {'user-agent': fake_useragent.UserAgent().random}
params = {'employer_id': employers_id.values(), 'per_page': vacancies_on_page,
          'archive': False}
