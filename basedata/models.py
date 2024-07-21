import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, Mapped


basic = declarative_base()

class Users(basic):
    '''Таблица пользователей'''
    __tablename__ = 'users'

    id = sq.Column(sq.Integer, sq.Sequence('user_id_seq'), autoincrement="auto")
    id_tg = sq.Column(sq.BigInteger, primary_key=True)
    first_name = sq.Column(sq.Text)
    username = sq.Column(sq.Text)
    yandex_token = sq.Column(sq.Text, default=None)

    # Ссылки на другие таблицы: Словарь, список избранного, переводчик, винрейт слов, уведомления, действия, повторы слов
    userwords: Mapped['AllWords'] = relationship(back_populates='userwords', uselist=True, secondary='userword')
    favorite_words: Mapped['AllWords'] = relationship(back_populates='favorite_words', uselist=True, secondary='favoriteworduser')
    translatorword: Mapped['TranslatorWord'] = relationship(back_populates='user', uselist=False)
    winrate: Mapped['WinRateWord'] = relationship(back_populates='user', uselist=True)
    notification: Mapped['Notifications'] = relationship(back_populates='user', uselist=False)
    action: Mapped['ActionsUsers'] = relationship(back_populates='user', uselist=False)
    repeat: Mapped['RepeatWord'] = relationship(back_populates='user', uselist=True)
    repeats: Mapped['RepeatWords'] = relationship(back_populates='user', uselist=True)


class AllWords(basic):
    ''''Таблица всех слов'''
    __tablename__ = 'allwords'

    id = sq.Column(sq.Integer, primary_key=True)
    eng_word = sq.Column(sq.Text)
    ru_word = sq.Column(sq.Text)
    tr = sq.Column(sq.Text)

    # --- Ссылка на таблицу словаря и списка избранного ---
    userwords: Mapped['Users'] = relationship(back_populates='userwords', uselist=True, secondary='userword')
    favorite_words: Mapped['Users'] = relationship(back_populates='favorite_words', uselist=True, secondary='favoriteworduser')


class UserWord(basic):
    '''Таблица словарных слов пользователей'''
    __tablename__ = 'userword'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.BigInteger, sq.ForeignKey('users.id_tg', ondelete='CASCADE'))
    id_word = sq.Column(sq.BigInteger, sq.ForeignKey('allwords.id', ondelete='CASCADE'))


class FavoriteWordUser(basic):
    '''Таблица изранных слов пользователей'''
    __tablename__  = 'favoriteworduser'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.BigInteger, sq.ForeignKey('users.id_tg', ondelete='CASCADE'))
    id_word = sq.Column(sq.BigInteger, sq.ForeignKey('allwords.id', ondelete='CASCADE'))


class TranslatorWord(basic):
    '''Установка языка переводчика пользователей'''
    __tablename__  = 'translatorword'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.BigInteger, sq.ForeignKey('users.id_tg', ondelete='CASCADE'))
    language = sq.Column(sq.Text, default=None)

    # --- Ссылка на таблицу пользователей ---
    user: Mapped['Users'] = relationship(back_populates='translatorword', uselist=False)


class WinRateWord(basic):
    '''Таблица с процентами правильно отвеченных слов пользователями'''
    __tablename__ = 'winrateword'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.BigInteger, sq.ForeignKey('users.id_tg', ondelete='CASCADE'))
    answer = sq.Column(sq.Text)

    # --- Ссылка на таблицу пользователей ---
    user: Mapped['Users'] = relationship(back_populates='winrate', uselist=False)


class Notifications(basic):
    '''Таблица уведомлений'''
    __tablename__ = 'notifications'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.BigInteger, sq.ForeignKey('users.id_tg', ondelete='CASCADE'))
    notifications = sq.Column(sq.Text, default='no')

    # --- Ссылка на таблицу пользователей ---
    user: Mapped['Users'] = relationship(back_populates='notification', uselist=False)


class ActionsUsers(basic):
    '''Таблица информации о действиях пользователей'''
    __tablename__ = 'actionsusers'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.BigInteger, sq.ForeignKey('users.id_tg', ondelete='CASCADE'))
    action = sq.Column(sq.Text, default=None)

    # --- Ссылка на таблицу пользователей ---
    user: Mapped['Users'] = relationship(back_populates='action', uselist=False)


class RepeatWord(basic):
    """Кеш таблица для одного слова"""
    __tablename__ = 'repeatword'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.BigInteger, sq.ForeignKey('users.id_tg', ondelete='CASCADE'))
    id_word = sq.Column(sq.Integer)
    eng_word = sq.Column(sq.Text)
    ru_word = sq.Column(sq.Text)
    word1 = sq.Column(sq.Text)
    word2 = sq.Column(sq.Text)
    word3 = sq.Column(sq.Text)
    word4 = sq.Column(sq.Text)

    # --- Ссылка на таблицу пользователей ---
    user: Mapped['Users'] = relationship(back_populates='repeat', uselist=False)


class RepeatWords(basic):
    """Кеш таблица для нескольких слов"""
    __tablename__ = 'repeatwords'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.BigInteger, sq.ForeignKey('users.id_tg', ondelete='CASCADE'))
    id_word = sq.Column(sq.Integer)
    eng_word = sq.Column(sq.Text)
    ru_word = sq.Column(sq.Text)
    word1 = sq.Column(sq.Text)
    word2 = sq.Column(sq.Text)
    word3 = sq.Column(sq.Text)
    word4 = sq.Column(sq.Text)

    # --- Ссылка на таблицу пользователей ---
    user: Mapped['Users'] = relationship(back_populates='repeats', uselist=False)


