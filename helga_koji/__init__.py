import re
from txkoji import Connection
from txkoji.exceptions import KojiException
from twisted.internet import defer
from helga.plugins import Plugin, ResponseNotReady
from helga import log
from helga import settings
from helga_koji.actions import get_build
from helga_koji.actions import get_package
from helga_koji.actions import kojiweb
from helga_koji.actions import user_tasks
import helga_koji.signals

__version__ = '1.5.0'


logger = log.getLogger(__name__)


class MultiMatch(Plugin):
    """
    A plugin that can match several different "actions".

    This plugin will only trigger if a user directly messages us, or the user
    directly addresses us in a channel.

    If one of those conditions are met, this plugin will call each action's
    "match()" method. If we find a match, then we call self.run().
    """
    actions = ()

    # TODO: support COMMAND_PREFIX_BOTNICK
    prefix = re.compile("^%s[,:]? " % settings.NICK)

    def process(self, client, channel, nick, message):
        # If this is not a private message, we should only respond when the
        # user directly mentions our name.
        if channel != nick:
            if self.prefix.match(message):
                # Strip off our prefix so we can pass the main message string
                # through to action.match()
                message = self.prefix.sub('', message)
        for action in self.actions:
            m = action.match(message)
            if m:
                return self.run(client, channel, nick, message, action, m)


class HelgaKoji(MultiMatch):

    help = 'https://github.com/ktdreyer/helga-koji'

    actions = (get_build, get_package, kojiweb, user_tasks)

    def run(self, client, channel, nick, message, action, match):
        profile = 'brew'  # todo: make this configurable
        koji = Connection(profile)

        d = defer.succeed(koji)
        for callback in action.callbacks:
            d.addCallback(callback, match, client, channel, nick)
            d.addErrback(send_err, client, channel)
        raise ResponseNotReady


def send_err(e, client, channel):
    client.msg(channel, '%s: %s' % (e.type.__name__, e.value))
    # Provide the file and line number if this was an an unexpected error.
    if not isinstance(e.value, KojiException):
        tb = e.getBriefTraceback().split()
        client.msg(channel, str(tb[-1]))
