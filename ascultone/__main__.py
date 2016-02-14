#!/usr/bin/env python3
import logging
import yaml

from .irc import IrcBot

with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

logging.basicConfig(**config["logging"])
bot = IrcBot(config)

try:
    bot.mainloop()
finally:
    bot.quit(config.get("quit_message", config["realname"]))
