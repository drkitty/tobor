from __future__ import unicode_literals

import irc.client
from irc.client import NickMask
from itertools import ifilter
from sys import stderr

from config import USERNAME, PASSWORD
from plugins import PLUGINS


class Robot(object):
    def __init__(self):
        self.client = irc.client.IRC()
        self.server = self.client.server()

    def disconnect(self):
        stderr.write('Disconnecting...\n')
        self.client.disconnect_all()
        self.server.disconnect()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def connect(self):
        def handler_wrapper(func):
            def wrapped(connection, event):
                return func(connection, event)

            return wrapped

        stderr.write('Connecting...\n')
        self.server.connect('irc.freenode.net', 6667, USERNAME)
        stderr.write('Identifying...\n')
        self.server.privmsg('NickServ', 'identify {0}'.format(PASSWORD))

        self.client.add_global_handler('privmsg', self.privmsg_handler)
        self.client.add_global_handler('pubmsg', self.pubmsg_handler)

    def join(self, channel):
        self.server.join(channel)

    def handle_normal(self, msg, sender, channel=None):
        plugins = filter(lambda p: not p[0], PLUGINS)
        for _, func in plugins:
            response = func(msg, sender, channel)
            if response:
                return response

    def handle_mentioned(self, msg, sender, channel=None):
        splat = msg.split(None, 1)
        if len(splat) == 1:
            command = splat[0]
            rest = ''
        else:
            command, rest = splat

        plugin = next(ifilter(lambda t: t[0] == command, PLUGINS), None)
        if not plugin:
            return self.handle_normal(msg, sender, channel=None)

        response = plugin[1](rest, sender, channel)
        if response:
            return response

    def pubmsg_handler(self, connection, event):
        msg = event.arguments[0]
        sender = NickMask(event.source)
        channel = event.target

        splat = msg.split(':', 1)
        if len(splat) == 1:
            response = self.handle_normal(msg, sender, channel)
        elif len(splat) == 2 and splat[0].strip() == USERNAME:
            response = self.handle_mentioned(splat[1].lstrip(), sender,
                                             channel)

        if response:
            for line in response.split('\n'):
                self.server.privmsg(channel, sender.nick + ': ' + line)

    def privmsg_handler(self, connection, event):
        msg = event.arguments[0]
        sender = NickMask(event.source)

        response = self.handle_mentioned(msg, sender)
        if response:
            for line in response.split('\n'):
                self.server.privmsg(sender.nick, line)

    def go(self):
        stderr.write('Doing things...\n')
        self.client.process_forever()
