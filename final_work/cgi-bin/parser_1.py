#!/usr/bin/env python3

import cgi
import psycopg2
import requests

# Подключение к базе данных PostgreSQL
connection = psycopg2.connect(
    dbname='testdb', user='user', password='password', host='postgres', port="5432")
print("DB connected")

c = connection.cursor()

def create_table():
    c.execute('''
    CREATE TABLE IF NOT EXISTS parsing(
        name TEXT,
        salary TEXT,
        experience TEXT,
        employment TEXT,
        url TEXT,
        adress TEXT,
        area TEXT,
        requirment TEXT,
        responsibility TEXT,
        roles TEXT
    )
    ''')
    connection.commit()

def data_entry(name, salary, experience, employment, url, adress, area, requirment, responsibility, roles):
    c.execute('''
    INSERT INTO parsing(name, salary, experience, employment, url, adress, area, requirment, responsibility, roles)
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (name, salary, experience, employment, url, adress, area, requirment, responsibility, roles))
    connection.commit()

our_form = cgi.FieldStorage()

in_name = our_form.getfirst("in_name", "...")
_area = our_form.getfirst("_area", "113")
_published_at = our_form.getfirst("_published_at", "2000-01-01T00:00:00+0300")
_company_name = our_form.getfirst("_company_name", "")

print("Content-Type: text/html; charset=utf-8")
print()

# Защита от дураков
in_name = in_name.replace("<", "").replace(">", "").replace("()", "").replace("(", "").replace(")", "").replace("'", "").replace('"', "").replace("/", "")

def get_vacancies(keyword):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": keyword,
        "area": _area,  # ID (1 - Москва)(113 - Россия)
        "per_page": 100,  # Кол-во вакансий
    }
    headers = {
        "User-Agent": "Your User Agent",
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        vacancies = data.get("items", [])
        create_table()  # Создание бд
        for vacancy in vacancies:
            published_at = vacancy.get("published_at")
            if published_at >= _published_at:
                company_name = vacancy.get("employer", {}).get("name")
                if (_company_name in company_name) or (_company_name == ''):
                    vacancy_title = vacancy.get("name")
                    vacancy_salary = vacancy.get("salary")
                    vacancy_exp = vacancy.get("experience", {}).get("name")
                    vacancy_employment = vacancy.get("employment", {}).get("name")
                    vacancy_url = vacancy.get("alternate_url")
                    vacancy_raw = vacancy.get("address")
                    country = vacancy.get("area", {}).get("name")
                    requirement = vacancy.get("snippet", {}).get("requirement")
                    responsibility = vacancy.get("snippet", {}).get("responsibility")
                    professional_roles = vacancy.get("professional_roles", {})[0].get("name")
                    print(f"<br>Название: {vacancy_title}\n<br>")
                    print(f"Зарплата: {vacancy_salary}\n<br>") 
                    print(f"Опыт работы: {vacancy_exp}\n<br>Требования: {requirement}\n<br>Обязанности: {responsibility}\n<br>Роль: {professional_roles}\n<br>Дата и Время Публикации: {published_at}\n<br>Компания: {company_name}\n<br>График Работы: {vacancy_employment}\n<br>Регион: {country}\n<br>Адрес: {vacancy_raw}\n<br>URL: {vacancy_url}\n<br>")
                    print("<br>")
                    data_entry(str(vacancy_title), str(vacancy_salary), str(vacancy_exp), str(vacancy_employment), str(vacancy_url), str(vacancy_raw), str(country), str(requirement), str(responsibility), str(professional_roles))
        # закрытие бд
        c.close()
        connection.close()
    else:
        print(f"Request failed with status code: {response.status_code}")

# Использование
get_vacancies(in_name)