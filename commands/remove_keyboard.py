from telebot import TeleBot
from telebot.types import *

from botstate import BotState
from command import Command
from database import DataBase
from yandexdisk import YandexDisk


def do(bot: TeleBot, bot_state: BotState, message: Message, database: DataBase, ydisk: YandexDisk):
    bot.send_message(message.chat.id, "Клавиатура успешно удалена.", reply_markup=ReplyKeyboardRemove())

remove_keyboard_command = Command("remove_keyboard", "Удалить клавиатуру", do=do)

