#!/usr/bin/env python3


class CommandEvent(object):
    def __init__(self, bot, message, params):
        self.bot = bot
        self.message = message
        self.params = params

    @property
    def source(self):
        return None
