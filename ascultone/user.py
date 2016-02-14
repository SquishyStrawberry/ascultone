#!/usr/bin/env python3


class User(object):
    def __init__(self, nickname, hostname=None, username=None):
        self.nickname = nickname
        self.hostname = hostname
        self.username = username

    def __repr__(self):
        return "{}({!r}, {!r}, {!r})".format(self.__class__.__name__,
                                             self.nickname,
                                             self.hostname,
                                             self.username)
