from telebot import TeleBot
from telebot.types import *

from botstate import BotState
from command import Command
from database import DataBase
from yandexdisk import YandexDisk


def send_photo(bot: TeleBot, bot_state: BotState, message: Message, database: DataBase, ydisk: YandexDisk, is_canceled: bool = False):
    state_additional = bot_state.get_state(message.from_user.id)["additional"]
    keyboard = None
    if is_canceled:
        keyboard = state_additional["keyboard"]["with_cancel"]
    else:
        keyboard = state_additional["keyboard"]["normal"]
    photo = database.get_random_photos(1)
    if len(photo) > 0:
        photo = photo[0]
        photo_url = ydisk.disk.get_download_link(photo["filepath"])
        bot.send_photo(message.chat.id, photo_url, reply_markup=keyboard, caption="https://www.instagram.com/{}".format(photo["source"]))
    else:
        bot.send_message(message.chat.id, "Фотографии закончились :(\nВведите /help, остановите эту хреновину.")
        bot_state.add_state(message.chat.id, "help")

    return photo


def send_canceled_photo(photo, bot: TeleBot, bot_state: BotState, message: Message, ydisk: YandexDisk):
    state_additional = bot_state.get_state(message.from_user.id)["additional"]
    keyboard = state_additional["keyboard"]["normal"]
    photo_url = ydisk.disk.get_download_link(photo["filepath"])
    bot.send_photo(message.chat.id, photo_url, reply_markup=keyboard)


def do(bot: TeleBot, bot_state: BotState, message: Message, database: DataBase, ydisk: YandexDisk):
    bot.send_message(message.chat.id,
                     "Начата проверка фотографий. Чтобы закончить проверку, введите любую другую команду (/help).")
    print("{}: started photo validation".format(message.from_user.username))
    state_additional = bot_state.get_state(message.from_user.id)["additional"]

    keyboard1 = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard1.row("Подтвердить", "Удалить")
    keyboard1.row("Отменить последнее решение")
    keyboard2 = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard2.row("Подтвердить", "Удалить")
    state_additional["keyboard"] = {"with_cancel": keyboard1, "normal": keyboard2}
    photo = send_photo(bot, bot_state, message, database, ydisk)

    state_additional["last_photo"] = photo



def echo(bot: TeleBot, bot_state: BotState, message: Message, database: DataBase, ydisk: YandexDisk):
    state_additional = bot_state.get_state(message.from_user.id)["additional"]
    last_photo = state_additional["last_photo"]
    # state_additional["penult_photo"] =
    if message.text == "Подтвердить":
        database.set_photo_status(last_photo["hash"], "checked", message.from_user.id)
        state_additional["penult_photo"] = last_photo
        state_additional["last_photo"] = send_photo(bot, bot_state, message, database, ydisk, True)
    elif message.text == "Удалить":
        database.set_photo_status(last_photo["hash"], "deleted", message.from_user.id)
        state_additional["penult_photo"] = last_photo
        state_additional["last_photo"] = send_photo(bot, bot_state, message, database, ydisk, True)
    elif message.text == "Отменить последнее решение":
        database.set_photo_status(state_additional["penult_photo"]["hash"], "unchecked", message.from_user.id)
        send_canceled_photo(state_additional["penult_photo"], bot, bot_state, message, ydisk)
        state_additional["last_photo"] = state_additional["penult_photo"]
    else:
        bot.send_message(message.chat.id,
                         "Введите нормальный ответ или воспользуйтесь другой командой (/help), чтобы отменить действие этой.")


def end(bot: TeleBot, bot_state: BotState, message: Message, database: DataBase, ydisk: YandexDisk):
    print("{}: ended photo validation".format(message.from_user.username))
    state_additional = bot_state.get_state(message.from_user.id)["additional"]
    state_additional["keyboard"]["normal"] = ReplyKeyboardRemove()
    state_additional["keyboard"]["with_cancel"] = ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Подождите немного. Выполняются изменения...", reply_markup=ReplyKeyboardRemove())
    photos_for_deleting = database.get_photos_for_deleting(message.from_user.id)
    for photo in photos_for_deleting:
        if ydisk.disk.exists(photo["filepath"]):
            ydisk.disk.remove(photo["filepath"])
        if photo["source"] is not None:
            database.increment_insta_stat(photo["source"], "unapproved_photos")
        database.delete_photo(photo["hash"])
    bot.send_message(message.chat.id, "Ваши правки применены.")


check_photos_command = Command("check_photos", "Валидация контента", do=do, is_admin_command=True,
                               echo=echo, need_answer=True, end=end)
