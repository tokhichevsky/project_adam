import os

from telebot import TeleBot
from telebot.types import *

from botstate import BotState
from command import Command
from database import DataBase
from yandexdisk import YandexDisk


def send_photos(bot: TeleBot, database: DataBase, ydisk: YandexDisk):
    photos = database.get_random_photos(10, "checked")
    if len(photos) > 0:
        for photo in photos:
            if ydisk.disk.exists(photo["filepath"]):
                bot.send_photo(os.environ["CHANNEL"], ydisk.disk.get_download_link(photo["filepath"]),
                               disable_notification=True)
                database.set_photo_status(photo["hash"], "published")
    else:
        print("The photos are over")


def do(bot: TeleBot, bot_state: BotState, message: Message, database: DataBase, ydisk: YandexDisk):
    photos = database.get_random_photos(10, "checked")
    if len(photos) > 0:
        for photo in photos:
            if ydisk.disk.exists(photo["filepath"]):
                bot.send_photo(os.environ["CHANNEL"], ydisk.disk.get_download_link(photo["filepath"]),
                               disable_notification=True)
                database.set_photo_status(photo["hash"], "published")
    else:
        bot.send_message(message.chat.id, "Фотографии закончились :(")


publish_command = Command("publish", "Опубликовать контент немедленно", do=do, is_admin_command=True)
