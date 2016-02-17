#!/usr/bin/env python3


class Channel(object):
    def __init__(self, name):
        self.name = name

    def say(self, bot, text):
        bot.send_privmsg(self.name, text)

    def act(self, bot, text):
        bot.send_action(self.name, text)
