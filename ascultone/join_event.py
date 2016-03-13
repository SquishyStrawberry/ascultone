#!/usr/bin/env python3


class JoinEvent(object):
    def __init__(self, bot, sender, channel):
        self.bot = bot
        self.sender = sender
        self.channel = channel
