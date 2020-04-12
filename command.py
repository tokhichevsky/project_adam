from typing import Callable, Any

from telebot import TeleBot
from telebot.types import Message

# from botstate import BotState
from database import DataBase
from yandexdisk import YandexDisk


class Command:
    def __init__(self, command: str, short_description: str, do: Callable[[], Any], echo: Callable[[], Any] = None,
                 is_admin_command: bool = False, need_answer: bool = False, end: Callable[[], Any] = None):
        self.echo = echo
        self.__do = do
        self.command = command
        self.short_description = short_description
        self.is_admin_command = is_admin_command
        self.need_answer = need_answer
        self.end = end
        self.tools = None

    def do(self, bot: TeleBot, bot_state, message: Message, database: DataBase, ydisk: YandexDisk):
        self.tools = {
            "bot": bot,
            "bot_state": bot_state,
            "database": database,
            "ydisk": ydisk
        }
        if (not self.is_admin_command) or (self.is_admin_command and database.is_admin(message.from_user.id)):
            last_state = bot_state.get_state(message.chat.id)
            if last_state is not None and last_state["command"].end is not None:
                last_command = last_state["command"]
                last_command.end(bot, bot_state, message, database, ydisk)
            bot_state.add_state(message.chat.id, self.command)
            self.__do(bot, bot_state, message, database, ydisk)
        else:
            bot.send_message(message.chat.id, "Данная команда вам не доступна!")

    def stop(self, message: Message):
        if self.tools is not None:
            self.tools["bot_state"].add_state(message.chat.id, "help")

    # def end(self, bot: TeleBot, bot_state, message: Message, database: DataBase, ydisk: YandexDisk):


class CommandList:
    def __init__(self, *args):
        self.__commands = []
        for command in args:
            self.add(command)

    def __len__(self):
        return len(self.__commands)

    def __getitem__(self, command_index):
        if type(command_index) == str:
            for command in self.__commands:
                if command.command == command_index:
                    return command
        elif type(command_index) == int:
            return self.__commands.__getitem__(command_index)
        return None

    def __contains__(self, item):
        if type(item) == str:
            return self.__getitem__(item) is not None
        elif type(item) == Command:
            return item in self.__commands

    def add(self, command: Command):
        if command.command not in self:
            self.__commands.append(command)

    def get_na_commands(self):
        na_commands = CommandList()
        for command in self.__commands:
            if command.need_answer:
                na_commands.add(command)
        return na_commands
