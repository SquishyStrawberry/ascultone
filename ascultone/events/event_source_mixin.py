#!/usr/bin/env python3


class EventSourceMixin(object):
    @property
    def source(self):
        if self.message.params[0] == self.bot.nickname:
            return self.message.sender.nickname
        else:
            return self.message.params[0]
