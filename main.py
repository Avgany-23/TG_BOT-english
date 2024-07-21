from scripts.bd_func import TableUsers
from scripts.main_func import *
import telebot
import json
import os
import re


path = os.path.join(os.getcwd(), 'basedata\info_bd.json')
with open(path, encoding='utf-8') as f:
    token = json.load(f)['token_bot']

bot = telebot.TeleBot(token)             # Подключение к Боту


# --- Обработка команды /start ---
@bot.message_handler(commands=['start'])
def start_bot(message):
    """Главное меню бота"""
    # --- Сохранение пользователя в Базу Данных ---
    users = TableUsers(path)
    users.add_user(message.chat.id, message.from_user.first_name, message.from_user.username)

    # --- Вывод главного меню бота ---
    inline_main_menu(message.chat.id, bot)


# ------- Ответы с Inline клавиатуры -------
@bot.callback_query_handler(func=lambda cb: True)
def callback_inline_start(callback):
    id_user = callback.message.chat.id
    id_mess = callback.message.message_id
    cb_dat = callback.data
    # ----------- Действия -----------
    if cb_dat == 'main menu':                                   # Вызов главного меню
        inline_main_menu(id_user, bot, show='replace', id_mess=id_mess)
    if cb_dat == 'none':                                        # Для пустых Inline клавиш
        empty_response(bot, callback.id)
    if cb_dat in ('learn', 'next word'):                        # Вызов меню с изучением слов
        inline_learn_all_words(id_user, bot, id_mess)
    if cb_dat in ('add dict', 'add favorite'):                  # Добавляет слова в словарь или избранное
        add_word_to_user(id_user, cb_dat, callback.id, bot)
    if re.findall(r'word\d{1,2}', cb_dat):                      # Для определения правильности ответа на перевод слова
        check_word_learn(id_user, bot, cb_dat, callback.id)
    if cb_dat == 'next word repeat':                            # Для вывода следующего слова пользователя при повторении
        inline_learn_all_words(id_user, bot, id_mess, repeat=True)
    if cb_dat in ('user_dict'):                                 # Вызов меню добавленных пользователем слов
        inline_add_words(id_user, bot, id_mess)
    if cb_dat in ('words_dict', 'words_favorite'):              # Вызов меню словаря / списка избранного
        inline_learn_user_words(id_user, id_mess, bot, cb_dat)
    if re.findall(r'action[123_]{1,2}', cb_dat):                # Вызов меню выбора количества слова
        user_dict_count(id_user, id_mess, bot, cb_dat)
    if re.findall(r'repeat\d{2}|all', cb_dat):                  # Повторение или просмотра пользовательских слов
        user_words_repeat_or_print(id_user, id_mess, bot, cb_dat, callback.id)

    if re.findall(r'del_.+', cb_dat):                           # Для удаления слов
        delete_user_word(id_user, bot, id_mess, cb_dat, callback.id)
    if cb_dat == 'save_yandex':                                 # Для отправки слов на Яндекс диск
        inline_save(bot, id_user, id_mess)
    if cb_dat in ('save_yandex dict', 'save_yandex favotire'):  # Меню для выбора отправляемых слов
        send_yand_disk(id_user, bot, id_mess, cb_dat, callback.id)
    if cb_dat == 'translate':                                   # Меню для выбора перевода слов в чате
        inline_translator_menu(bot, id_user, id_mess)
    if cb_dat in ('ru-en', 'en-ru'):                            # Установка языка перевода. Оповещение бота об этом
        translate_installation(bot, id_user, cb_dat)
    if cb_dat == 'info':                                        # Вывод информации пользователя
        info_user(bot, id_user, id_mess)
    if cb_dat == 'notif':                                       # Меню с установкой уведомлений
        inline_notifications(bot, id_user, id_mess)
    if re.findall(r'time\d{2}|off_notif', cb_dat):              # Установка/отключение уведомлений
        notifications(id_user, bot, cb_dat, callback.id)


# ------- Ответы на текстовые сообщения пользователя -------
@bot.message_handler(content_types=['text'])
def another_message(message):
    text = message.text
    id_user = message.chat.id

    # ----------- Действия -----------
    if re.findall(r'token:\s*[\w]{5,}\s*', text):           # Если пользователь пытается добавить токен
        add_yandex_token(bot, text, id_user)
    else:
        translate_chat_word(bot, id_user, text)             # Перевод слов

bot.polling()