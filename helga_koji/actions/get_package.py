import re
from twisted.internet import defer


def match(message):
    """
    "ceph package"

    :returns: a package name if we matched, or None if not.
    """
    pattern = re.compile('^(\S+) package\??$')
    m = re.match(pattern, message)
    if not m:
        return
    return m.group(1)  # eg. "ceph"


@defer.inlineCallbacks
def describe_package(koji, package_name, client, channel, nick):
    """
    Describe this package in a message
    """
    package = yield koji.getPackage(package_name)
    if not package:
        tmpl = '{nick}, I could not find a package for "{package}" at {url}.'
        msg = tmpl.format(nick=nick, package=package_name, url=koji.weburl)
        defer.returnValue(msg)
    tmpl = '{nick}, {package} is {url}'
    msg = tmpl.format(nick=nick, package=package_name, url=package.url)
    defer.returnValue(msg)


def send_message(message, shortname, client, channel, nick):
    """
    Send a message to channel.
    """
    if message:
        client.msg(channel, message)


# List of callbacks to fire on a match:
callbacks = (describe_package, send_message)
