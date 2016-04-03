#!/usr/bin/env python3

from .event_source_mixin import EventSourceMixin


class CommandEvent(EventSourceMixin):
    def __init__(self, bot, message, params):
        self.bot = bot
        self.message = message
        self.params = params

    @property
    def sender(self):
        return self.message.sender

    @property
    def param_text(self):
        return " ".join(self.params)
