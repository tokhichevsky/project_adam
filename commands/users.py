from telebot import TeleBot
from telebot.types import *

from botstate import BotState
from command import Command
from database import DataBase
from yandexdisk import YandexDisk


def do(bot: TeleBot, bot_state: BotState, message: Message, database: DataBase, ydisk: YandexDisk):
    bot.send_message(message.chat.id, database.get_records("users", ["telegram_id", "username", "is_admin"]))


users_command = Command("users", "Список пользователей", do=do, is_admin_command=True)
