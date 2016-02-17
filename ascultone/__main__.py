#!/usr/bin/env python3
import logging
import yaml

from .ascultone import Ascultone

with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

logging.basicConfig(**config["logging"])
bot = Ascultone(config)

bot.start()
