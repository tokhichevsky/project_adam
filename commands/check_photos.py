from telebot import TeleBot
from telebot.types import *

from botstate import BotState
from command import Command
from database import DataBase
from yandexdisk import YandexDisk


def send_photo(bot: TeleBot, message: Message, database: DataBase, ydisk: YandexDisk, is_canceled: bool = False):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Подтвердить", "Удалить")
    if is_canceled:
        keyboard.row("Отменить последнее решение")
    photo = database.get_random_photos(1)[0]
    photo_url = ydisk.disk.get_download_link(photo["filepath"])
    bot.send_photo(message.chat.id, photo_url, reply_markup=keyboard)
    return photo


def send_canceled_photo(photo, bot: TeleBot, message: Message, ydisk: YandexDisk):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Подтвердить", "Удалить")
    photo_url = ydisk.disk.get_download_link(photo["filepath"])
    bot.send_photo(message.chat.id, photo_url, reply_markup=keyboard)


def do(bot: TeleBot, bot_state: BotState, message: Message, database: DataBase, ydisk: YandexDisk):
    bot.send_message(message.chat.id,
                     "Начата проверка фотографий. Чтобы закончить проверку, введите любую другую команду (/help).")
    photo = send_photo(bot, message, database, ydisk)
    state_additional = bot_state.get_state(message.chat.id)["additional"]
    state_additional["last_photo"] = photo


def echo(bot: TeleBot, message: Message, state_additional, database: DataBase, ydisk: YandexDisk):
    last_photo = state_additional["last_photo"]
    # state_additional["penult_photo"] =
    if message.text == "Подтвердить":
        database.set_photo_status(last_photo["hash"], "checked", message.from_user.id)
        state_additional["penult_photo"] = last_photo
        state_additional["last_photo"] = send_photo(bot, message, database, ydisk, True)
    elif message.text == "Удалить":
        database.set_photo_status(last_photo["hash"], "deleted", message.from_user.id)
        state_additional["penult_photo"] = last_photo
        state_additional["last_photo"] = send_photo(bot, message, database, ydisk, True)
    elif message.text == "Отменить последнее решение":
        database.set_photo_status(state_additional["penult_photo"]["hash"], "unchecked", message.from_user.id)
        send_canceled_photo(state_additional["penult_photo"], bot, message, ydisk)
        state_additional["last_photo"] = state_additional["penult_photo"]
    else:
        bot.send_message(message.chat.id,
                         "Введите нормальный ответ или воспользуйтесь другой командой (/help), чтобы отменить действие этой.")


def end(bot: TeleBot, message: Message, state_additional, database: DataBase, ydisk: YandexDisk):
    bot.send_message(message.chat.id, "Подождите немного. Выполняются изменения...", reply_markup=ReplyKeyboardRemove())
    photos_for_deleting = database.get_photos_for_deleting()
    for photo in photos_for_deleting:
        ydisk.disk.remove(photo["filepath"])
        database.delete_photo(photo["hash"])
    bot.send_message(message.chat.id, "Ваши правки применены.")


check_photos_command = Command("check_photos", "Валидация контента", do=do, is_admin_command=True,
                               echo=echo, need_answer=True, end=end)
