#!/usr/bin/env python3
import logging

from .server import Server
from .user import User


class Message(object):
    logger = logging.getLogger(__name__)

    def __init__(self, line):
        self.line = line
        if line[0] == ":":
            line = line[1:]
            sender, line = line.split(" ", 1)
            if sender.find("!") == -1:
                # This is a probably server
                self.sender = Server(sender)
            else:
                # This is an user
                nick, user = sender.split("!", 1)
                user, host = user.split("@", 1)
                self.sender = User(nick, host, user)
        line = line.split(" ", 1)
        self.command = line[0]
        self.params = []
        if len(line) > 1:
            found_colon = False
            for param in line[1].split():
                if param and param[0] == ":":
                    param = param[1:]
                    found_colon = True
                    self.params.append("")
                if found_colon:
                    self.params[-1] += " " + param
                else:
                    self.params.append(param)

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.line)
