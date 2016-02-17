#!/usr/bin/env python3
import re
import logging

from .user import User
from .server import Server
from .channel import Channel


class Message(object):
    logger = logging.getLogger(__name__)
    message_regexp = re.compile(
        "(?::(?P<prefix>(?P<servername>[^\x00\r\n :@!]+)"
        "|(?P<nickname>[^\x00\r\n :!]+)"
        "!(?P<username>[^\x00\r\n :@]+)"
        "@(?P<hostname>[^\x00\r\n :]+)) )?"
        "(?P<command>[^\x00\r\n :]+)"
        "(?: (?P<params>[^\x00\r\n]+))?"
    )

    def __init__(self, sender, command, params):
        self.sender = sender
        self.command = command
        self.params = params

    def __repr__(self):
        return "{}({!r}, {!r}, {!r})".format(self.__class__.__name__,
                                             self.sender,
                                             self.command,
                                             self.params)

    def find_source(self, bot):
        assert self.command == "PRIVMSG"
        if self.params[0] == bot.nickname:
            return self.sender
        else:
            return Channel(self.params[0])

    @classmethod
    def from_line(cls, line):
        msg_match = cls.message_regexp.match(line)
        if msg_match is None:
            # Usually if we can't match a line it's an error in my RegExp
            cls.logger.debug("Could not match line '%s'", line)
            return None
        if msg_match.group("servername") is not None:
            sender = Server(msg_match.group("servername"))
        else:
            sender = User(msg_match.group("nickname"),
                          msg_match.group("hostname"),
                          msg_match.group("username"))
        params = []
        colon_params = []
        found_colon = False
        for param in msg_match.group("params").split(" "):
            if param.startswith(":"):
                found_colon = True
                param = param[1:]
            if found_colon:
                colon_params.append(param)
            else:
                params.append(param)
        params.append(" ".join(colon_params))
        return cls(sender, msg_match.group("command"), params)
