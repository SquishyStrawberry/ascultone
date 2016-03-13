#!/usr/bin/env python3
import random


def init_module(bot):
    bot.register_join(greeter)


def greeter(event):
    module_config = event.bot.config["module_config"]["greeter"]
    if event.sender.nickname == event.bot.nickname:
        event.bot.send_action(event.channel,
                              random.choice(module_config["on_self_join_messages"]))
    else:
        msg = random.choice(module_config["on_other_join_messages"])
        event.bot.send_action(event.channel,
                              msg.format(user=event.sender.nickname))
