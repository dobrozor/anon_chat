import config
import telebot
from telebot import types

from config import MEDIA
from database import Database
from telebot.types import InputMediaPhoto, InputMediaVideo

import sms

db = Database('db.db')
bot = telebot.TeleBot(config.TOKEN)
admin_chat = config.ADMIN_CHAT
media_chat = config.MEDIA
error_chat = config.ERROR

def main_menu(): #Меню поиск собеседника
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton(sms.key_search)
    item2 = types.KeyboardButton(sms.key_set_pol)
    markup.add(item1, item2)
    return markup

def stop_dialog(): #Меню если ты в чате
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton(sms.key_go_profile)
    item2 = types.KeyboardButton(sms.key_stop_dialog)
    markup.add(item1, item2)
    return markup

def menu_search(): #Меню если ты в чате
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton(sms.key_search_boy)
    item2 = types.KeyboardButton(sms.key_search_girl)
    item3 = types.KeyboardButton(sms.key_search_random)
    item4 = types.KeyboardButton(sms.key_menu)
    markup.add(item1, item2, item3, item4)
    return markup

def stop_search(): #Меню если ты в поиске
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton(sms.key_stop_search)
    markup.add(item1)
    return markup

@bot.message_handler(commands = ['start'])
def start(message):
    chat_info = db.get_active_chat(message.chat.id)
    if chat_info != False:
        db.delete_chat(chat_info[0])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item2 = types.KeyboardButton(sms.key_search_dialog)
        item1 = types.KeyboardButton(sms.key_menu)
        markup.add(item1, item2)

        bot.send_message(chat_info[1], sms.leave_chat, reply_markup=markup)
        bot.send_message(message.chat.id, sms.leaving_chat, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, sms.no_sms)

        markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
        item1 = types.KeyboardButton(sms.key_im_boy)
        item2 = types.KeyboardButton(sms.key_im_girl)
        markup.add(item1, item2)
        bot.send_message(message.chat.id, sms.set_gender, reply_markup = markup)

@bot.message_handler(commands=['error'])
def report_problem(message):
    chat_info = db.get_active_chat(message.chat.id)
    if chat_info != False:
        db.delete_chat(chat_info[0])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item2 = types.KeyboardButton(sms.key_search_dialog)
        item1 = types.KeyboardButton(sms.key_menu)
        markup.add(item1, item2)
        bot.send_message(chat_info[1], sms.leave_chat, reply_markup=markup)
        bot.send_message(message.chat.id, sms.leaving_chat, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, sms.no_sms)
    # Запрашиваем у пользователя о проблеме
    bot.send_message(message.chat.id, "Напишите проблему:")
    # Устанавливаем состояние ожидания ответа от пользователя
    bot.register_next_step_handler(message, process_problem)
def process_problem(message):
    # Пересылаем сообщение в заданный чат
    bot.send_message(config.ADMIN_CHAT,
                     f"Проблема от {message.from_user.username}: {message.text}", message_thread_id=error_chat)
    bot.send_message(message.chat.id, "Ваша проблема была отправлена.")


@bot.message_handler(func=lambda message: message.text == sms.key_menu or message.text == '/menu')
def menu(message):
    chat_info = db.get_active_chat(message.chat.id)
    if chat_info != False:
        db.delete_chat(chat_info[0])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item2 = types.KeyboardButton(sms.key_search_dialog)
        item1 = types.KeyboardButton(sms.key_menu)
        markup.add(item1, item2)

        bot.send_message(chat_info[1], sms.leave_chat, reply_markup=markup)
        bot.send_message(message.chat.id, sms.leaving_chat, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, sms.no_sms)

    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton(sms.key_search)
    item2 = types.KeyboardButton(sms.key_set_pol)
    markup.add(item1, item2)
    bot.send_message(message.chat.id, sms.key_menu.format(message.from_user), reply_markup = markup)


@bot.message_handler(func=lambda message: message.text == sms.key_stop_dialog or message.text == '/stop' or message.text == '/next')
def stop(message):
    chat_info = db.get_active_chat(message.chat.id)
    if chat_info != False:
        db.delete_chat(chat_info[0])
        markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
        item2 = types.KeyboardButton(sms.key_search_dialog)
        item1 = types.KeyboardButton(sms.key_menu)
        markup.add(item1, item2)

        bot.send_message(chat_info[1], sms.leave_chat, reply_markup = markup)
        bot.send_message(message.chat.id, sms.leaving_chat, reply_markup = markup)
    else:
        bot.send_message(message.chat.id, sms.no_sms)

#=================================================#

@bot.message_handler(commands=['test'])
def test(message):
    try:
        bot.send_message(admin_chat, "тест")
    except Exception as e:
        print(f"Ошибка: {e}")

#=====================Меню кнопок============================#
@bot.message_handler(content_types = ['text'])
def bot_message(message):
    if message.chat.type == 'private':

        #Поиск собеседника по полу
        if message.text == sms.key_search:
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            bot.send_message(message.chat.id, sms.ho_search, reply_markup=menu_search())

        # Следующий диалог
        elif message.text == sms.key_search_dialog:
            user_info = db.get_chat()
            chat_two = user_info[0]
            if db.create_chat(message.chat.id, chat_two) == False:
                db.add_queue(message.chat.id, db.get_gender(message.chat.id))
                bot.send_message(message.chat.id, sms.searhing, reply_markup=stop_search())
            else:
                mess = sms.on_search
                bot.send_message(message.chat.id, mess, reply_markup=stop_dialog())
                bot.send_message(chat_two, mess, reply_markup=stop_dialog())

        # Поиск по парню
        elif message.text == sms.key_search_boy:
            user_info = db.get_gender_chat('male')
            chat_two = user_info[0]
            if db.create_chat(message.chat.id, chat_two) == False:
                db.add_queue(message.chat.id, db.get_gender(message.chat.id))
                bot.send_message(message.chat.id, sms.searhing, reply_markup=stop_search())
            else:
                mess = sms.on_search
                bot.send_message(message.chat.id, mess, reply_markup=stop_dialog())
                bot.send_message(chat_two, mess, reply_markup=stop_dialog())

        # Поиск по девушке
        elif message.text == sms.key_search_girl:
            user_info = db.get_gender_chat('female')
            chat_two = user_info[0]
            if db.create_chat(message.chat.id, chat_two) == False:
                db.add_queue(message.chat.id, db.get_gender(message.chat.id))
                bot.send_message(message.chat.id, sms.searhing, reply_markup=stop_search())
            else:
                mess = sms.on_search
                bot.send_message(message.chat.id, mess, reply_markup=stop_dialog())
                bot.send_message(chat_two, mess, reply_markup=stop_dialog())

        # Поиск рандомно
        elif message.text == sms.key_search_random:
            user_info = db.get_chat()
            chat_two = user_info[0]
            if db.create_chat(message.chat.id, chat_two) == False:
                db.add_queue(message.chat.id, db.get_gender(message.chat.id))
                bot.send_message(message.chat.id, sms.searhing, reply_markup=stop_search())
            else:
                mess = sms.on_search
                bot.send_message(message.chat.id, mess, reply_markup=stop_dialog())
                bot.send_message(chat_two, mess, reply_markup=stop_dialog())

        #Изменение гендера
        elif message.text == sms.key_set_pol:
            db.remove_gender(message.chat.id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton(sms.key_im_boy)
            item2 = types.KeyboardButton(sms.key_im_girl)
            markup.add(item1, item2)
            bot.send_message(message.chat.id, sms.ho_gender, reply_markup=markup)

        # Настройка пола Я парень
        elif message.text == sms.key_im_boy:
            if db.set_gender(message.chat.id, 'male'):
                bot.send_message(message.chat.id, sms.gender_like, reply_markup=main_menu())
            else:
                bot.send_message(message.chat.id, sms.gender_dislike, reply_markup=main_menu())

        # Настройка пола Я девушка
        elif message.text == sms.key_im_girl:
            if db.set_gender(message.chat.id, 'female'):
                bot.send_message(message.chat.id, sms.gender_like, reply_markup=main_menu())
            else:
                bot.send_message(message.chat.id, sms.gender_dislike, reply_markup=main_menu())

        #Остановить поиск
        elif message.text == sms.key_stop_search:
            db.delete_queue(message.chat.id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bot.send_message(message.chat.id, sms.ho_search, reply_markup=menu_search())

        #Сказать свой профиль
        elif message.text == sms.key_go_profile:
            chat_info = db.get_active_chat(message.chat.id)
            if chat_info != False:
                if message.from_user.username:
                    bot.send_message(chat_info[1], '🗣 Это мой ' + '[юзернейм](http://t.me/' + message.from_user.username + '/) ' + 'кликай', parse_mode='Markdown')
                    bot.send_message(message.chat.id, sms.go_profile)
                else:
                    bot.send_message(message.chat.id, sms.error_profile)
            else:
                bot.send_message(message.chat.id, sms.no_sms)

        #И если ни одно сообщение не подходит то выводим вы не в чате
        else:
            if db.get_active_chat(message.chat.id) != False:
                chat_info = db.get_active_chat(message.chat.id)
                bot.send_message(chat_info[1], message.text)
            else:
                bot.send_message(message.chat.id, sms.no_sms)
#======================Сообщения=======================================
@bot.message_handler(content_types=['sticker', 'voice', 'photo', 'video', 'video_note', 'text'])
def handle_media(message):
    media_group = []

    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)

        if chat_info is not False:
            if message.content_type == 'text':
                text_message = message.text

            # Обработка медиа
            if message.content_type == 'sticker':
                bot.send_sticker(chat_info[1], message.sticker.file_id)
            elif message.content_type == 'voice':
                bot.send_voice(chat_info[1], message.voice.file_id)
            elif message.content_type == 'photo':
                file_id = message.photo[-1].file_id  # Берем файл с максимальным качеством
                media_group.append(InputMediaPhoto(file_id))
            elif message.content_type == 'video':
                file_id = message.video.file_id
                media_group.append(InputMediaVideo(file_id))
            elif message.content_type == 'video_note':
                file_id = message.video_note.file_id
                bot.send_video_note(chat_info[1], file_id)

            # Если есть медиа в группе, отправляем их
            if media_group:
                bot.send_media_group(chat_info[1], media=media_group)

                #bot.send_message(admin_chat, 'Фото от @' + message.from_user.username, message_thread_id=media_chat)
                bot.send_media_group(admin_chat, media=media_group, message_thread_id=media_chat)

            # Отправляем текстовое сообщение, если оно есть
            if 'text_message' in locals():
                bot.send_message(chat_info[1], '^)')
        else:
            bot.send_message(message.chat.id, sms.no_sms)


if __name__ == '__main__':
    bot.polling()