#!/usr/bin/env python3
import eventlet; eventlet.monkey_patch()
import importlib
import logging
import os
import sqlite3
import sys
import traceback

from .irc import IrcBot
from .channel import Channel
from .command_event import CommandEvent
from .join_event import JoinEvent


class Ascultone(IrcBot):
    logger = logging.getLogger(__name__)
    def __init__(self, config):
        super().__init__(config)
        self.on_join  = []
        self.commands = {}
        self.triggers = {}
        self.modules  = []
        self.database = sqlite3.connect(config["database"])
        self.cursor   = self.database.cursor()

    def register_join(self, function):
        self.on_join.append(function)

    def register_command(self, command, function):
        self.commands[command] = function

    def quit(self, reason=None):
        super().quit(reason)
        self.database.commit()

    def start(self):
        if not self.connected:
            self._connect()
        for module in self.config.get("modules", []):
            self.load_file(module)
        try:
            self.mainloop()
        finally:
            self.quit(self.config.get("quit_message", self.config["realname"]))

    def load_file(self, filename):
        self.logger.info("Loading module '%s'...", filename)
        # This whole song and dance is to that `importlib.import_module`
        # imports the files from the module folder too.
        filedir = os.path.abspath(os.path.dirname(filename))
        modulename = os.path.splitext(os.path.basename(filename))[0]
        sys.path.insert(0, filedir)
        try:
            module = importlib.import_module(modulename)
        except Exception as e:
            # I don't want to stop the whole bot for a faulty module
            self.logger.error("Failed to load module '%s'!", filename)
            traceback.print_exc()
        else:
            self.modules.append(module)
            module.init_module(self)
        # But of course we don't want modules to import from the module folder
        # after loading one module.
        sys.path = sys.path[1:]

    def _handle_message(self, message):
        if message.command == "JOIN":
            self.logger.info("Dispatching JOIN handlers...")
            for func in self.on_join:
                sender = message.sender
                channel = Channel(message.params[0])
                eventlet.spawn_n(
                    func,
                    JoinEvent(self, sender, channel)
                )
        elif message.command == "PRIVMSG":
            message_split = message.params[1].split()
            if message_split[0] in (self.nickname, self.nickname + "!"):
                command = message_split[1]
                params = message_split[2:]
                self.logger.info("Got command '%s' with params %s",
                                 command, params)
                if command in self.commands:
                    eventlet.spawn_n(
                        self.commands[command],
                        CommandEvent(self, message, params)
                    )
