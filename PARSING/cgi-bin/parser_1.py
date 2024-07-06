#!/usr/bin/env python3

import cgi
import requests
import psycopg2
from psycopg2 import sql

connection = psycopg2.connect(
    host='postgres',  # Имя хоста PostgreSQL сервера
    port=5432,
    user='chara',  # Имя пользователя PostgreSQL
    password='password',  # Пароль пользователя PostgreSQL
    database='db'  # Имя базы данных
)

def create_table():
    with connection:
        with connection.cursor() as cursor:
            # Проверить и удалить старую таблицу parsing_old, если существует
            cursor.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'parsing_old') THEN
                    DROP TABLE parsing_old;
                END IF;
            END $$;
            """)
            
            # Переименовать старую таблицу parsing, если существует
            cursor.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'parsing') THEN
                    ALTER TABLE parsing RENAME TO parsing_old;
                END IF;
            END $$;
            """)
            
            # Создание новой таблицы с типами данных TEXT
            create_table_query = """
            CREATE TABLE IF NOT EXISTS parsing (
                id VARCHAR(255) PRIMARY KEY,
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
            """
            cursor.execute(create_table_query)
        connection.commit()

def data_entry(id, name, salary, experience, employment, url, adress, area, requirment, responsibility, roles):
    with connection:
        with connection.cursor() as cursor:
            insert_query = sql.SQL("""
            INSERT INTO parsing (id, name, salary, experience, employment, url, adress, area, requirment, responsibility, roles)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                salary = EXCLUDED.salary,
                experience = EXCLUDED.experience,
                employment = EXCLUDED.employment,
                url = EXCLUDED.url,
                adress = EXCLUDED.adress,
                area = EXCLUDED.area,
                requirment = EXCLUDED.requirment,
                responsibility = EXCLUDED.responsibility,
                roles = EXCLUDED.roles
            """)
            cursor.execute(insert_query, (id, name, salary, experience, employment, url, adress, area, requirment, responsibility, roles))
        connection.commit()

our_form = cgi.FieldStorage()

in_name = our_form.getfirst("in_name", "...")
_area = our_form.getfirst("_area", "113")
_published_at = our_form.getfirst("_published_at", "2000-01-01T00:00:00+0300")
_company_name = our_form.getfirst("_company_name", "")

print("Content-Type: text/html; charset=utf-8")
print()

# Защита от XSS
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
                    vacancy_id = vacancy.get("id")
                    vacancy_title = vacancy.get("name")
                    vacancy_salary = vacancy.get("salary")
                    vacancy_exp = vacancy.get("experience", {}).get("name")
                    vacancy_employment = vacancy.get("employment", {}).get("name")
                    vacancy_url = vacancy.get("alternate_url")
                    vacancy_raw = vacancy.get("address")
                    country = vacancy.get("area", {}).get("name")
                    requirement = vacancy.get("snippet", {}).get("requirement")
                    responsibility = vacancy.get("snippet", {}).get("responsibility")
                    professional_roles = vacancy.get("professional_roles", [])[0].get("name")
                    print(f"ID: {vacancy_id}\n<br>Название: {vacancy_title}\n<br>")
                    print(f"Зарплата: {vacancy_salary}\n<br>")
                    print(f"Опыт работы: {vacancy_exp}\n<br>Требования: {requirement}\n<br>Обязанности: {responsibility}\n<br>Роль: {professional_roles}\n<br>Дата и Время Публикации: {published_at}\n<br>Компания: {company_name}\n<br>График Работы: {vacancy_employment}\n<br>Регион: {country}\n<br>Адрес: {vacancy_raw}\n<br>URL: {vacancy_url}\n<br>")
                    print("<br>")
                    data_entry(int(vacancy_id), str(vacancy_title), str(vacancy_salary), str(vacancy_exp), str(vacancy_employment), str(vacancy_url), str(vacancy_raw), str(country), str(requirement), str(responsibility), str(professional_roles))
        # Закрытие соединения
        connection.close()
    else:
        print(f"Request failed with status code: {response.status_code}")

# Использование
get_vacancies(in_name)
