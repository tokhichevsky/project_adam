from telebot import TeleBot
from telebot.types import *

from botstate import BotState
from command import Command
from database import DataBase
from yandexdisk import YandexDisk


def do(bot: TeleBot, bot_state: BotState, message: Message, database: DataBase, ydisk: YandexDisk):
    users = database.get_records("users", ["telegram_id", "username", "is_admin"])
    text = "{:<12} {:<18} {:<8}".format("telegram_id", "username", "is_admin")
    for user in users:
        text += "\n{:<12} {:<18} {:<8}".format(user["telegram_id"], user["username"], user["is_admin"])
    print("{}: requested a list of users".format(message.from_user.username))
    bot.send_message(message.chat.id, text)


users_command = Command("users", "Список пользователей", do=do, is_admin_command=True)
