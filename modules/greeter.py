#!/usr/bin/env python3
import random


def init_module(bot):
    bot.register_join(greeter)


def greeter(bot, sender, channel):
    module_config = bot.config["module_config"]["greeter"]
    if sender.nickname == bot.nickname:
        bot.send_action(channel,
                        random.choice(module_config["on_self_join_messages"]))
    else:
        msg = random.choice(module_config["on_other_join_messages"])
        bot.send_action(channel,
                        msg.format(user=sender.nickname))
