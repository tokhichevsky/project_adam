from telebot import TeleBot
from telebot.types import *

from botstate import BotState
from command import Command
from database import DataBase
from yandexdisk import YandexDisk


def do(bot: TeleBot, bot_state: BotState, message: Message, database: DataBase, ydisk: YandexDisk):
    user: User = message.from_user
    database.add_user(user.id, user.username)
    bot.send_message(message.chat.id, "Введите /help, чтобы увидеть список доступных вам команд.")

start_command = Command("start", "Описание бота", do=do)

