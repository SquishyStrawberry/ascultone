#!/usr/bin/env python3


class CommandEvent(object):
    def __init__(self, bot, message, params):
        self.bot = bot
        self.message = message
        self.params = params

    @property
    def source(self):
        if self.message.params[0] == self.bot.nickname:
            return self.message.sender.nickname
        else:
            return self.message.params[0]

    @property
    def param_text(self):
        return " ".join(self.params)
