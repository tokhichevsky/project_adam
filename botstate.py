from command import CommandList


class BotState:
    def __init__(self, saved_commands: CommandList):
        self.__states = {}
        self.__saved_commands = saved_commands
        # self.__all_commands = all_commands

    def add_state(self, chat_id: int, command: str, additional: dict = {}):
        if command in self.__saved_commands:
            self.__states[chat_id] = {"command": self.__saved_commands[command], "additional": additional}
        elif chat_id in self.__states.keys():
            self.__states.pop(chat_id)

    def get_state(self, chat_id: int):
        return self.__states.get(chat_id)
