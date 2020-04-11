from telebot import TeleBot
from telebot.types import *

from botstate import BotState
from command import Command
from database import DataBase
from yandexdisk import YandexDisk


def do(bot: TeleBot, bot_state: BotState, message: Message, database: DataBase, ydisk: YandexDisk):
    bot.send_message(message.chat.id, "Введите логин пользователя")


def echo(bot: TeleBot, bot_state: BotState, message: Message, database: DataBase, ydisk: YandexDisk):
    result = database.set_admin(message.text)
    bot.send_message(message.chat.id, result)


set_admin_command = Command("set_admin", "Сделать пользователя администратором", do=do,
                            is_admin_command=True, need_answer=True,
                            echo=echo)
