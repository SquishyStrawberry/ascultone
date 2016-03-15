#!/usr/bin/env python3
import random


def init_module(bot):
    bot.register_command("attack", command_attack)


def command_attack(event):
    messages = event.bot.config["module_messages"]["attacker"]
    attack = random.choice(messages["attacks"])
    event.bot.send_action(event.source,
                          attack.format(target=event.param_text))
