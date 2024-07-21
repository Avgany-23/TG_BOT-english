import os
import random
from sqlalchemy.orm import sessionmaker
import json
from basedata.models import *
from sqlalchemy import select, create_engine, delete, func, desc



class Session():
    """Общий класс для подключения к Базе Данных"""

    def __init__(self, path):
        '''Путь к Базе Данных'''
        with open(path, encoding='utf-8') as f:
            bd = json.load(f)['postgreSQL']
        puthBD = f"{bd['bd']}://{bd['login']}:{bd['password']}@localhost:5432/{bd['name_bd']}"
        engine = create_engine(puthBD)
        self.session = sessionmaker(engine)()


class TableUsers(Session):
    """Класс для работы с таблице Users"""

    def info_user(self, id_user):
        '''Получение информации о пользователе'''
        users = [(i.id_tg, i.first_name, i.username, i.yandex_token)
                 for i in self.session.query(Users).filter(Users.id_tg == id_user)]
        self.session.close()
        return users

    def add_user(self, id, first_name, last_name):
        '''Добавление id, языка переводчки (none), уведомлений (none), действия (none) пользователя в БД'''
        users = self.session.query(Users).filter(Users.id_tg == id).all()
        if not users:
            self.session.add(Users(id_tg=id, first_name=first_name, username=last_name))    # Добавление в Users
            self.session.add(TranslatorWord(id_user=id))                                    # Добавление в переводчик
            self.session.add(Notifications(id_user=id))                                     # Добавление в уведомления
            self.session.add(ActionsUsers(id_user=id))                                 # Добавление в действия
        self.session.commit(), self.session.close()

    def add_token(self, id_user, token):
        '''Добавление токена пользователю в БД'''
        users = self.session.query(Users).filter(Users.id_tg == id_user).update({'yandex_token': token})
        self.session.commit(), self.session.close()


class TableAllWords(Session):
    """Класс для работы с таблицей общих слов"""

    def random_words(self):
        '''Изъятие случайных слов из БД
        Функция вернет список случайных слов из БД'''
        rand = self.session.query(AllWords).order_by(func.random()).limit(4)
        self.session.close()
        return [(el.eng_word, ',  '.join(el.ru_word.split(', ')[:2]), el.id) for el in rand]


class TableUserWords(Session):
        """Клас для работы с добавленными пользователями словами"""

        def user_words(self, id_user, tab, randoms, count=100 * 100):
            '''Изъятие случайных пользовательских слов из БД
            Функция вернет список пользовательских слов из БД'''
            # --- Выбираем таблицу ---
            table = {'_' not in tab: UserWord, '_' in tab: FavoriteWordUser}[1]

            # --- Получение слов ---
            if randoms:
                usersw = ((self.session.query(table.id_word, table.id_user, AllWords.eng_word, AllWords.ru_word))
                          .join(AllWords, table.id_word == AllWords.id)
                          .order_by(func.random())
                          .limit(count).all())
            else:
                usersw = ((self.session.query(table.id_word, table.id_user, AllWords.eng_word, AllWords.ru_word))
                          .join(AllWords, table.id_word == AllWords.id)
                          .order_by(desc(table.id))
                          .limit(count).all())
            self.session.close()
            return usersw

        def user_count_words(self, id_user, tab):
            """Получение информации о количестве слов"""
            table = {'dict': UserWord, 'favorite': FavoriteWordUser}[tab]
            count = self.session.query(sq.func.count(table.id_user)).filter(table.id_user == id_user)
            self.session.close()
            return count.scalar()

        def add_word_user(self, id_word, id_user, tab):
            '''Добавление слов пользователю в словарь или в избранное
            Функция вернёт True, если слово добавится, False - если слово уже добавлено'''
            table = {'add dict': UserWord, 'add favorite': FavoriteWordUser}[tab]
            usersw = self.session.query(table).filter(table.id_word == id_word, table.id_user == id_user)
            if not [(el.id_word, el.id_user) for el in usersw]:
                users = self.session.add(table(id_word=id_word,
                                               id_user=id_user))
                self.session.commit(), self.session.close()
                return True
            self.session.close()
            return False

        def delete_word(self, id_user, tab, count):
            '''Функция для удаления слов из словаря или избранного'''
            table = {'dict': UserWord, 'favorite': FavoriteWordUser}[tab]
            if count == 'all':
                self.session.query(table).filter(table.id_user == id_user).delete()
            elif count == 'one':
                id_word = self.session.query(RepeatWord.id_word).filter(RepeatWord.id_user == id_user).scalar()
                self.session.query(table).filter(table.id_user == id_user, table.id_word == id_word).delete()
            self.session.commit(), self.session.close()


class TableTranslator(Session):
    '''Класс для работы таблицы переводчкика'''

    def info_user_language(self, id_user):
        "Получение информации о установленном пользователе языке"
        language = self.session.query(TranslatorWord).filter(TranslatorWord.id_user == id_user)
        return [i.language for i in language]

    def add_language(self, id_user, language):
        """Функция для обновления языка перевода пользователя"""
        self.session.query(TranslatorWord).filter(TranslatorWord.id_user == id_user).update({'language': language})
        self.session.commit(), self.session.close()


class TableStatistics(Session):
    """Класс для работы со статистикой переведённых слов пользователей"""

    def add_result_selection(self, id_user, result):
        """Функция сохраняет результат выбора ответа пользователя при переводе слов: верно - неверно"""
        self.session.add(WinRateWord(id_user=id_user, answer=result))
        self.session.commit(), self.session.close()

    def show_result_user(self, id_user):
        """Функция выводит правильные и неправильные ответы пользователя"""
        # Количество правильных слов
        tr = (self.session.query(sq.func.count(WinRateWord.id_user)).
              filter(WinRateWord.id_user == id_user, WinRateWord.answer == 'true'))
        # Количество неправильных слов
        fl = (self.session.query(sq.func.count(WinRateWord.id_user)).
              filter(WinRateWord.id_user == id_user, WinRateWord.answer == 'false'))
        self.session.close()
        if tr.scalar() == fl.scalar() == 0: return None
        try: return tr.scalar() / (fl.scalar() + tr.scalar())
        except ZeroDivisionError: return 0


class TableNotification(Session):
    """Класс для работы с таблицей уведомлений пользователей"""

    def notif_users(self, id_user=None, all_users=True):
        '''Функция для получения информации об уведомлениях пользователей
        Если all = True, значит информация по уведомлениям берётся о всех пользователях, False - об одном'''
        if all_users: respons = self.session.query(Notifications)
        else: respons = self.session.query(Notifications).filter(Notifications.id_user == id_user)
        self.session.close()
        return [(i.id_user, i.notifications) for i in respons]

    def update_notif(self, id_user, notif):
        '''Функция для установки и отключения уведомлений'''
        self.session.query(Notifications).filter(Notifications.id_user == id_user).update({'notifications': notif})
        self.session.commit(), self.session.close()


class TableRepeatWord(Session):
        """Класс для работы с таблицей изучаемыми слов пользователя """

        def get_repeat_words(self, id_user):
            """Функция для получения ВСЕХ угадываемых слов и их перевода"""
            word = self.session.query(RepeatWord).filter(RepeatWord.id_user == id_user).all()
            self.session.close()
            return [(i.id_word, i.eng_word, i.ru_word, i.word1, i.word2, i.word3, i.word4) for i in word]


        def save_repeat_word(self, id_word, id_user, eng_word, ru_word, word1, word2, word3, word4):
            """Функция для записи угадываемого слова"""
            self.session.add(RepeatWord(id_word=id_word,
                                         id_user=id_user,
                                         eng_word=eng_word,
                                         ru_word=ru_word,
                                         word1=word1,
                                         word2=word2,
                                         word3=word3,
                                         word4=word4))
            self.session.commit(), self.session.close()

        def delete_repeat_word(self, id_user):
            """Функция для удаления слова для повторения"""
            (self.session.query(RepeatWord)
             .filter(RepeatWord.id_user == id_user)
             .delete())
            self.session.commit(), self.session.close()


class TableRepeatWords(Session):
    """Класс для работы с таблицей повторяемыми словами пользователя """

    def get_repeat_words(self, id_user):
        """Функция для получения ОДНОГО угадываемого слова и общее количество слов пользователя в RepetWords"""
        word = (self.session.query(RepeatWords)
                .filter(RepeatWords.id_user == id_user, RepeatWords.id_word != 0)
                .limit(1).scalar())
        self.session.close()
        count = (self.session.query(func.count(RepeatWords.id_user))
                 .filter(RepeatWords.id_user == id_user, RepeatWords.id_word != 0).scalar())
        if word:
            return (word.id_word, word.eng_word, word.ru_word, word.word1, word.word2, word.word3, word.word4), count
        return [None, 0]

    def save_repeat_words(self, words: list[tuple]):
        """Функция для записи ВСЕХ угадываемых слов. Функция принимает список кортежей, где каждый кортеж содержит
        в себе id слова, id_tg пользователе, слово на английском и его перевод на русском. Функция записывает
        слова в таблицу RepeatWord: первые 4 аргумента - элементы текущего кортежа, вторые 4 аргумента - 3
        случайных слов на русском из других полученных кортежей и 1 слово на русском из текущего кортежа"""

        for i, row in enumerate(words):
            other_tuple = words[:i] + words[i + 1:]  # Все кортежи, кроме текущего
            random.shuffle(other_tuple)
            result = other_tuple[:3] + [row]  # Получение 4 кортежей с текущим кортежем
            random.shuffle(result)  # Перемешивание слов
            self.session.add(RepeatWords(id_word=row[0],
                                         id_user=row[1],
                                         eng_word=row[2],
                                         ru_word=row[3],
                                         word1=result[0][3],
                                         word2=result[1][3],
                                         word3=result[2][3],
                                         word4=result[3][3]))
        self.session.commit(), self.session.close()

    def delete_repeat_words(self, id_user, id_word=None):
        """Функция для удаления записанных слов для повторения
           Если id_word не указан, то удаляются все слова, если указан - одно слово"""
        if id_word is None:
            (self.session.query(RepeatWords)
             .filter(RepeatWords.id_user == id_user)
             .delete())
        else:
            (self.session.query(RepeatWords)
             .filter(RepeatWords.id_user == id_user, RepeatWords.id_word == id_word)
             .delete())
        self.session.commit(), self.session.close()


class TableAction(Session):
    """"Класс для работы с таблицей текущих действий пользователей"""

    def save_action(self, id_user, action):
        """Функция для сохранения действия"""
        self.session.query(ActionsUsers).filter(ActionsUsers.id_user==id_user).update({'action': action})
        self.session.commit(), self.session.close()

    def get_user_action(self, id_user):
        """Функция для получения действия пользователя"""
        check_action = self.session.query(ActionsUsers.action).filter(ActionsUsers.id_user == id_user).scalar()
        self.session.close()
        return check_action