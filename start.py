import os
import re

import telebot

from availablecommands import commands
from botstate import BotState
from database import DataBase
from yandexdisk import YandexDisk

database = DataBase()
# print(database.set_admin("olynkascheeva"))
ydisk = YandexDisk(token=os.environ["YADISKTOKEN"])
bot = telebot.TeleBot(os.environ['TOKEN'])
bot_state = BotState(saved_commands=commands.get_na_commands())


#
#
@bot.message_handler(content_types=["text"])
def answer_commands(message):
    try:
        global bot_state
        found_command = re.findall(r"^/([A-z]+)", message.text)
        state = bot_state.get_state(message.chat.id)

        if len(found_command) > 0 and found_command[0] in commands:
            commands[found_command[0]].do(bot, bot_state, message, database, ydisk)
        elif state:
            state["command"].echo(bot, bot_state, message, database, ydisk)
        else:
            bot.send_message(message.chat.id, "Не понимаю Вас, воспользуйтесь /help, чтобы выбрать команду.")
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка.\n"+str(e))
        bot.send_message(message.chat.id, "Воспользуйтесь /help, чтобы выбрать команду.")




if __name__ == '__main__':
    bot.polling()
