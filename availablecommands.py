import re
import time

from telebot import TeleBot
from telebot.types import *

# from botstate import BotState
from command import Command, CommandList
from database import DataBase
from commands import *

# DOS


#
#
#
#
# def do_words(bot: TeleBot, bot_state, message: Message, database: DataBase):
#     bot.send_message(message.chat.id, database.get_records("words", ))
#
#
# def do_addword(bot: TeleBot, bot_state, message: Message, database: DataBase):
#     bot.send_message(message.chat.id, "Напишите слово так, чтобы все буквы кроме ударной были строчными.")
#
#
#
#
# def do_addwordsfromfile(bot: TeleBot, bot_state, message: Message, database: DataBase):
#     bot.send_message(message.chat.id, "Введите имя файла со словами")
#
#
#
# def do_exercise(bot: TeleBot, bot_state, message: Message, database: DataBase):
#     state_additional = bot_state.get_state(message.chat.id)["additional"]
#     state_additional["last_word"] = database.get_word(message.from_user.id)
#     # last_word = state_additional["last_word"]
#     bot.send_message(message.chat.id, "Чтобы прекратить выполнение задания введите любую другую команду (/help)")
#     bot.send_message(message.chat.id,
#                      "Поставьте ударение в слове «{}»".format(state_additional["last_word"]["word"].lower()))
#
#
#
#
# # ANSWERS
#
# def answer_addword(bot: TeleBot, message: Message, state_additional, database: DataBase):
#     result = database.add_word(message.text)
#     bot.send_message(message.chat.id, result)
#
#
#
#
#
# def answer_addwordsfromfile(bot: TeleBot, message: Message, state_additional, database: DataBase):
#     try:
#         f = open(message.text, 'r', encoding='utf-8')
#         text = f.read()
#         words = re.sub(r"(?:\n| +|,){1,}", " ", text).split()
#         for word in words:
#             result = database.add_word(word)
#             bot.send_message(message.chat.id, result)
#             time.sleep(0.1)
#     except Exception as e:
#         bot.send_message(message.chat.id, e)
#
#
# def answer_exercise(bot: TeleBot, message: Message, state_additional, database: DataBase):
#     plus_level = 0
#     last_word = state_additional["last_word"]
#
#     if last_word["word"] == message.text:
#         bot.send_message(message.chat.id, "Правильно!")
#         if last_word["level"] != database.get_num_levels():
#             plus_level = 1
#         database.set_word_level(message.from_user.id, last_word["word_id"], last_word["level"] + plus_level)
#     else:
#         bot.send_message(message.chat.id, "Неправильно! Верный ответ: «{}»".format(last_word["word"]))
#         database.set_word_level(message.from_user.id, last_word["word_id"], 1)
#     # bot.send_message(message.chat.id, "Чтобы прекратить выполнение задания введите любую другую команду (/help)")
#     state_additional["last_word"] = database.get_word(message.from_user.id)
#     bot.send_message(message.chat.id,
#                      "Поставьте ударение в слове «{}»".format(state_additional["last_word"]["word"].lower()))
#
#
#
#
#
#
#
#


def do_help(bot: TeleBot, bot_state, message: Message, database: DataBase, ydisk):
    is_admin = database.is_admin(message.from_user.id)
    help_str = ""
    for command in commands:
        if not command.is_admin_command or (command.is_admin_command and is_admin):
            help_str += "/{} - {}\n".format(command.command, command.short_description)
    bot.send_message(message.chat.id, help_str)

help_command = Command("help", "Список доступных команд", do=do_help)


commands = CommandList(start_command,
                       help_command,
                       users_command,
                       set_admin_command,
                       check_photos_command,
                       # Command("get_image_info", "Получить информацию об изображении", do=do_get_image_info,
                       #         need_answer=True,
                       #         echo=answer_get_image_info),
                       # Command("publish", "Опубликовать контент немедленно", do=do_publish, is_admin_command=True),
                       # Command("words", "Список слов", is_admin_command=True, do=do_words),
                       # Command("addword", "Добавить слово вида 'окнО'", do=do_addword, is_admin_command=True,
                       #         need_answer=True, echo=answer_addword),
                       # Command("addwordsfromfile", "Добавить слова из файла", do=do_addwordsfromfile,
                       #         is_admin_command=True, need_answer=True, echo=answer_addwordsfromfile),
                       check_photos_command,
                       # Command("exercise", "Начать тест на ударения", do=do_exercise, need_answer=True,
                       #         echo=answer_exercise)
                       )
