#!/usr/bin/env python3
import collections
import logging
import socket

from .message import Message


class IrcBot(object):
    logger = logging.getLogger(__name__)
    CHUNK_SIZE = 1 << 11  # 2048

    def __init__(self, config):
        self.nickname = None  # We define this in `_connect`
        self.config = config
        self.connected = False
        self.linebuffer = collections.deque()
        self.channels = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _get_line(self):
        while not self.linebuffer:
            chunk = self.socket.recv(self.CHUNK_SIZE)
            for line in chunk.splitlines():
                if line:
                    self.linebuffer.append(line)
        return self.linebuffer.popleft().decode("utf-8")

    def _get_message(self):
        msg = Message.from_line(self._get_line())
        self.logger.debug("Got message '%s'", msg)
        return msg

    def _respond_to_ping(self, message):
        assert message.command == "PING"
        self.logger.info("Responding to PING '%s'", message.params[0])
        return self._send("PONG :{}".format(message.params[0]))

    def _connect(self):
        if self.connected:
            return
        self.logger.info("Connecting...")
        self.socket.connect((self.config["hostname"], self.config["port"]))
        if isinstance(self.config["nickname"], str):
            self.nickname = self.config["nickname"]
        else:
            nickname_iterator = iter(self.config["nickname"])
            self.nickname = next(nickname_iterator)
        self._send("NICK {}".format(self.nickname))
        self._send("USER {} 0 * :{}".format(self.config["username"],
                                            self.config["realname"]))
        while True:
            message = self._get_message()
            if message.command == "PING":
                self._respond_to_ping(message)
            elif message.command == "001":
                self.logger.info("Connected")
                return
            elif message.command == "433":
                self.logger.debug("Old nickname '%s' in use",
                                  self.nickname)
                if isinstance(self.config["nickname"], str):
                    self.logger.debug("Appending '_' to old nickname")
                    self.nickname += "_"
                else:
                    self.logger.debug("Trying new nickname from list '%s'",
                                      self.config["nickname"])
                    try:
                        self.nickname = next(nickname_iterator)
                    except StopIteration:
                        self.nickname += "_"
                self.logger.info("Switching to new nickname '%s'",
                                 self.nickname)
                self._send("NICK {}".format(self.nickname))

    def _send(self, text):
        if not text.endswith("\r\n"):
            text += "\r\n"
        self.socket.send(text.encode("utf-8"))

    def _handle_message(self, message):
        # As you can guess, this is just to be overriden
        pass

    def send_privmsg(self, recipient, text):
        return self._send("PRIVMSG {} :{}".format(recipient, text))

    def send_action(self, recipient, text):
        return self.send_privmsg(recipient, "\x01ACTION " + text)

    def join_channel(self, channel):
        if channel in self.channels:
            return
        self._send("JOIN {}".format(channel))
        self.channels.append(channel)

    def mainloop(self):
        for channel in self.config["channels"]:
            self.logger.info("Joining channel '%s'", channel)
            self.join_channel(channel)
        while True:
            message = self._get_message()
            if message.command == "PING":
                self._respond_to_ping(message)
            else:
                self._handle_message(message)

    def quit(self, reason=None):
        if reason is None:
            self._send("QUIT")
        else:
            self._send("QUIT :{}".format(reason))

    def start(self):
        if not self.connected:
            self._connect()
        try:
            self.mainloop()
        finally:
            self.quit(self.config.get("quit_message", self.config["realname"]))
