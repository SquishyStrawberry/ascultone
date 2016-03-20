#!/usr/bin/env python3

from .event_source_mixin import EventSourceMixin


class PrivmsgEvent(EventSourceMixin):
    def __init__(self, bot, message):
        self.bot = bot
        self.message = message

    @property
    def sender(self):
        return self.message.sender

    @property
    def text(self):
        return self.message.params[1]
