from telebot import TeleBot
from telebot.types import *

from botstate import BotState
from command import Command
from database import DataBase
from yandexdisk import YandexDisk

def do(bot: TeleBot, bot_state: BotState, message: Message, database: DataBase, ydisk: YandexDisk):
    bot.send_message(message.chat.id,
                     "Напишите SQL запрос на изменение БД. Запросы для получения информации не работают!")

def echo(bot: TeleBot, bot_state: BotState, message: Message, database: DataBase, ydisk: YandexDisk):
    result = database.execute(message.text)
    bot.send_message(message.chat.id, result)

execute_command = Command("execute", "Выполнить SQL запрос на изменение", do=do, is_admin_command=True,
                               need_answer=True, echo=echo)
