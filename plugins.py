from __future__ import unicode_literals

from config import OWNER


def repeat(rest, sender, channel):
    return rest


def elipsis(msg, sender, channel):
    if msg.strip() == '...':
        return '...'

def die(msg, sender, channel):
    if sender.nick == OWNER:
        exit(0)


PLUGINS = [
    ('die', die),
    ('repeat', repeat),
    (None, elipsis),
]
