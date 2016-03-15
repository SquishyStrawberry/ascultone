#!/usr/bin/env python3
import random


def init_module(bot):
    bot.register_join(handler_greet)


def handler_greet(event):
    messages = event.bot.config["module_messages"]["greeter"]
    if event.sender.nickname == event.bot.nickname:
        event.bot.send_action(event.channel, messages["announce_arrival"])
    else:
        greeting = random.choice(messages["greetings"])
        event.bot.send_action(event.channel,
                              greeting.format(nick=event.sender.nickname))
