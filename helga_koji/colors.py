"""
IRC color formatting.

helga.settings.SERVER['TYPE'] must be "irc".

TODO: support other chat protocols
"""


def red(text):
    """ Return this text formatted red """
    return '\x0304%s\x03' % text


def orange(text):
    """ Return this text formatted orange (olive) """
    return '\x0307%s\x03' % text


def brown(text):
    """ Return this text formatted brown (maroon) """
    return '\x0305%s\x03' % text


def green(text):
    """ Return this text formatted green """
    return '\x0303%s\x03' % text


def blue(text):
    """ Return this text formatted blue """
    return '\x0302%s\x03' % text


def purple(text):
    """ Return this text formatted purple """
    return '\x0306%s\x03' % text
