#!/usr/bin/env python3
import logging
import re

from .irc import IrcBot
from .channel import Channel


class Ascultone(IrcBot):
    logger = logging.getLogger(__name__)
    command_validator = re.compile(
        r"^\w+$"
    )

    def __init__(self, config):
        super().__init__(config)
        self.on_join = []
        self.commands = {}
        self.triggers = {}

    def register_join(self, function):
        self.on_join.append(function)

    def register_command(self, command, function):
        assert self.command_validator.match(command) is not None
        self.commands[command] = function

    def register_trigger(self, trigger, function):
        self.triggers[re.compile(trigger)] = function

    def quit(self, reason=None):
        super().quit(reason)

    def _handle_message(self, message):
        if message.command == "JOIN":
            for func in self.on_join:
                sender = message.sender
                channel = Channel(message.params[0])
                func(self, sender, channel)
        elif message.command == "PRIVMSG":
            command_match = re.match(r"{}!?"
                                     r"\s+(?P<command>\w+)"
                                     r"(?: (?P<params>.+))?"
                                     .format(self.nickname),
                                     message.params[1])
            if command_match is not None:
                group_dict = command_match.groupdict()
                params = (group_dict["params"] or "").split(" ")
                self.logger.info("Got command '%s' with params %s",
                                 group_dict,
                                 (group_dict["params"] or "").split(" "))
                if group_dict["command"] in self.commands:
                    self.commands[group_dict["command"]](
                        self,
                        message.find_source(self),
                        message.sender,
                        params
                    )
            else:
                for trigger, response in self.triggers.items():
                    if trigger.search(message.params[1]) is None:
                        continue
                    self.logger.info("Matched trigger '%s' to message '%s'",
                                     trigger.pattern,
                                     message.params[1])
                    response(
                        self,
                        message.find_source(self),
                        message.sender,
                        message.params[1]
                    )
                    break
