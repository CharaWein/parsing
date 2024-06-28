#!/usr/bin/env python3

import cgi

our_form = cgi.FieldStorage()

in_name = our_form.getfirst("in_name", "...")
_area = our_form.getfirst("_area", "113")
_published_at = our_form.getfirst("_published_at", "2000-01-01T00:00:00+0300")
_company_name = our_form.getfirst("_company_name", "")

print("Content-type: text/html")
print()

import requests

#Защита от дураков
in_name = in_name.replace("<", "")
in_name = in_name.replace(">", "")
in_name = in_name.replace("()", "")
in_name = in_name.replace("(", "")
in_name = in_name.replace(")", "")
in_name = in_name.replace("'", "")
in_name = in_name.replace('"', "")
in_name = in_name.replace("/", "")

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
        for vacancy in vacancies:
            published_at = vacancy.get("published_at")
            if published_at >= _published_at:
                company_name = vacancy.get("employer", {}).get("name")
                if (company_name == _company_name) or (_company_name == ''):
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
                    professional_roles = vacancy.get("professional_roles", {})[0].get("name")
                    print(f"ID: {vacancy_id}\n<br>Название: {vacancy_title}\n<br>")
                    print(f"Зарплата: {vacancy_salary}\n<br>") 
                    print(f"Опыт работы: {vacancy_exp}\n<br>Требования: {requirement}\n<br>Обязанности: {responsibility}\n<br>Роль: {professional_roles}\n<br>Дата и Время Публикации: {published_at}\n<br>Компания: {company_name}\n<br>График Работы: {vacancy_employment}\n<br>Регион: {country}\n<br>Адрес: {vacancy_raw}\n<br>URL: {vacancy_url}\n<br>")
                    print("<br>")
    else:
        print(f"Request failed with status code: {response.status_code}")


# Использование
get_vacancies(in_name)