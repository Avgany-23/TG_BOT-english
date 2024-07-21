import re
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, create_engine
from models import basic, AllWords


def get_info(info_puth):
    """Получение информации о Базе Данных и токена ТГ бота"""
    with open(info_puth, encoding='utf-8') as f:
        res = json.load(f)                                          # Извлечение информации из файла
        return (res['postgreSQL']['bd'],
                res['postgreSQL']['login'],
                res['postgreSQL']['password'],
                res['postgreSQL']['name_bd'],
                res['token_bot'])


def check_bd(puth):
    """Функция проверяет, существуют ли таблицы в БД. Принимает путь к Базе Данных - path параметр
    Если хоть 1 таблица с именем созданных моделей будет сущестсвовать, то выдаст ошибку, в ином случае вернёт True"""
    engine = create_engine(puth)
    with engine.connect() as conn:
        tables = []                                         # Список существующих таблиц
        for table in basic.__subclasses__():                # проход по всем созданным моделям
            table = table.__name__.lower()                  # Получение имён моделей (таблиц из файла models.py)

            if conn.execute(text("""SELECT EXISTS 
                                   (SELECT FROM information_schema.tables
                                    WHERE table_name = :table_name);"""), {'table_name': table}).scalar():
                tables.append(table)
        if tables:                                          # Если хоть одна таблица существует, то вызов исключения
            raise SystemExit(f"Таблица(ы) {', '.join(tables)} существует в указанной вами базе.\n"
                             f"Создание таблиц не произошло")
        return True                                         # Если ни одной таблицы не существует, то можно создавать БД


def create_bd(info_puth):
    '''Функция для создания базы данных'''
    engine = create_engine(info_puth)                               # Получение движка
    session = sessionmaker(engine)()                                # Подключение к сессии
    basic.metadata.drop_all(engine)                                 # Удаление таблиц с таким же именем, если они есть
    basic.metadata.create_all(engine)                               # Создание таблиц
    print('БД успешна создана')                                     # Оповещение об успешном создании БД
    session.commit(), session.close()                               # Коммит и закрытие сессии


def loads_words(info_puth, name_file='words.txt'):
    '''Функция загружает слова в базу данных'''
    engine = create_engine(info_puth)                                                   # Получение движка
    session = sessionmaker(engine)()                                                    # Подключение к сессии

    # --- Обработка файла и загрузка в Базу Данных ---
    with open(name_file, encoding='utf-8') as f:
        reader = f.readlines()
        for i, el in enumerate(reader, 1):
            eng = el.split()[0]                                                         # Слово на английском
            ru = re.findall(r'\]\s+([\w ,\(\)-\.\!\/]+)\s+Войти', el)[0]                # Слово на русском
            trz = el.split()[1]                                                         # Транскрипция
            session.add(AllWords(eng_word=eng, ru_word=ru, tr=trz))                     # Загрузка в бд
    session.commit(), session.close()                                                   # Коммит и закрытие сессии
    print('Слова успшешно загружены')                                                   # Оповещение


if __name__ == '__main__':
    # --- Получение данных о Базе Данных (название, логин, пароль) ---
    data_bd = get_info('info_bd.json')
    puth = f"{data_bd[0]}://{data_bd[1]}:{data_bd[2]}@localhost:5432/{data_bd[3]}"

    # --- Проверка наличия существующих баз в БД ---
    check = check_bd(puth)

    # --- Если ни одной таблицы в БД с названием моделей не существует, то создается новая база данных ---
    if check:
        create_bd(puth)         # Создание БД
        loads_words(puth)       # Загрузка слов в БД