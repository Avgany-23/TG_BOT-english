import sqlalchemy as sq
import sqlalchemy
import sqlalchemy.orm
from scripts.bd_func import *
import requests
import json
import os

path = os.path.join(os.getcwd(), 'basedata\info_bd.json')  # Для функций из bd_func

def save_words(user_id, bd):
    "Функция для сохранения слов в текстовый файл"
    table = {'dict': 'dict', 'favorite': 'favorite_'}[bd]
    words = TableUserWords(path).user_words(user_id, table, randoms=False)  # Изъятие пользовательских слов
    if not words:   # Если слов нет, то ничего не загружается
        return False
    with open(f"forprogramm/save{user_id}.txt", 'w', encoding='utf-8') as f:
        for i, word in enumerate(words, 1):
            f.write(f"{str(i) + ': ' + word[2]:<18} {word[3]}\n")
    return True

def create_folder_yandex(token, folder):
    "Функция для создания папки на яндекс диске"
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {'Authorization': token}
    params = {'path': folder}
    response = requests.put(url, headers=headers, params=params)
    return response.status_code

def put_yandex_data(yandex_token, user_id, bd):
    """Функция для отправки файла на яндекс диск"""
    # --- Сохранение слов в файл ---
    save_words(user_id, bd)
    if not save_words(user_id, bd):
        # --- Если список пуст, то ничего не загрузит
        table = {'dict': 'Ваш словарь пуст. Загружать нечего',
                 'favorite': 'Список избранного пуст. Загружать нечего'}[bd]
        return (table, 0)

    # --- Создание папки на диске ---
    while True:
        folder = "UserWords" + f"{user_id}" + f"{random.randint(0, 9999)}"
        create = create_folder_yandex(yandex_token, folder=folder)
        if create != 409:
            break

    # --- Получение ссылки на загрузку ---
    url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    headers = {'Authorization': yandex_token}
    params = {'path': f"{folder}/eng_words"}
    response = requests.get(url, headers=headers, params=params)

    # --- Отправка файла по полученной ссылке ---
    with open(f'forprogramm/save{user_id}.txt', 'rb') as file:
        response1 = requests.put(response.json()['href'], files={'file': file.read()})
    os.remove(f'forprogramm/save{user_id}.txt')
    return (f'Файл успешно загружен. Имя папки - {folder}', 1)

def check_connect_to_yandex_disk(yandex_token):
    """Проверка корректности токена"""
    response = requests.get('https://cloud-api.yandex.net/v1/disk/', headers={'Authorization': yandex_token})
    return response.status_code