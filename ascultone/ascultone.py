#!/usr/bin/env python3
import eventlet; eventlet.monkey_patch()
import glob
import importlib
import logging
import os
import sqlite3
import sys
import traceback

from .irc import IrcBot
from .channel import Channel
from .events import CommandEvent, JoinEvent, PrivmsgEvent
from .user import User


class Ascultone(IrcBot):
    logger = logging.getLogger(__name__)
    action_prefix = "\x0303\u200B"

    class flags:  # namespaces are one honking great idea!
        admin       = 1 << 0
        whitelisted = 1 << 1


    def __init__(self, config):
        self.logger.info("Expanding module list %s...", config["modules"])
        new_modules = []
        for module in config["modules"]:
            new_modules.extend(glob.glob(module))
        self.logger.info("New module list: %s", new_modules)
        config["modules"] = new_modules
        super().__init__(config)
        self.on_join    = []
        self.on_privmsg = []
        self.commands   = {}
        self.triggers   = {}
        self.modules    = []
        self.database   = sqlite3.connect(config["database"])
        self.cursor     = self.database.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS Flags"
            "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " user TEXT NOT NULL,"
            " flags UNSIGNED INTEGER)"
        )

    def send_action(self, recipient, text):
        return super().send_action(recipient, self.action_prefix + text)

    def register_join(self, function):
        self.on_join.append(function)

    def register_privmsg(self, function):
        self.on_privmsg.append(function)

    def register_command(self, command, function):
        self.commands[command] = function

    def quit(self, reason=None):
        super().quit(reason)
        self.database.commit()

    def add_flag(self, user, flag):
        if isinstance(flag, str):
            flag = getattr(self.flags, flag)
            assert isinstance(flag, int)
        if isinstance(user, User):
            user = user.nickname
        self.cursor.execute(
            "SELECT flags "
            "FROM Flags "
            "WHERE user = ?", (user,)
        )
        current_flags = self.cursor.fetchone()
        if current_flags is None:
            self.cursor.execute(
                "INSERT INTO Flags(user, flags) "
                "VALUES "
                "(?, ?)", (user, flag)
            )
        else:
            self.cursor.execute(
                "UPDATE Flags "
                "SET flags = ? "
                "WHERE user = ?", (current_flags[0] | flag, user)
            )

    def remove_flag(self, user, flag):
        if isinstance(flag, str):
            flag = getattr(self.flags, flag)
            assert isinstance(flag, int)
        if isinstance(user, User):
            user = user.nickname
        self.cursor.execute(
            "SELECT flags "
            "FROM Flags "
            "WHERE user = ?", (user,)
        )
        current_flags = self.cursor.fetchone()
        if current_flags is not None and current_flags[0] & flag:
            self.cursor.execute(
                "UPDATE Flags "
                "SET flags = ? "
                "WHERE user = ?", (current_flags[0] ^ flag, user)
            )

    def has_flag(self, user, flag):
        if isinstance(flag, str):
            flag = getattr(self.flags, flag)
            assert isinstance(flag, int)
        if isinstance(user, User):
            user = user.nickname
        self.cursor.execute(
            "SELECT flags "
            "FROM Flags "
            "WHERE user = ?", (user,)
        )
        current_flags = self.cursor.fetchone()
        print(bin(current_flags[0]), bin(flag))
        return current_flags is not None and current_flags[0] & flag

    # We can just OR multiple flags together
    add_flags = add_flag
    remove_flags = remove_flag
    has_flags = has_flag

    def start(self):
        if not self.connected:
            self._connect()
        for module in self.config.get("modules", []):
            self.load_file(module)
        try:
            self.mainloop()
        except KeyboardInterrupt:
            pass
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
            for handler in self.on_privmsg:
                eventlet.spawn_n(
                    handler,
                    PrivmsgEvent(self, message)
                )
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
