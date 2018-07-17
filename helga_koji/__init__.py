from txkoji import Connection
from txkoji import KojiException
from twisted.internet import defer
from helga.plugins import match, ResponseNotReady
from helga import log
from helga_koji.actions import get_build
from helga_koji.actions import get_package
from helga_koji.actions import user_tasks

__version__ = '1.1.0'


logger = log.getLogger(__name__)


def match_koji(message):
    for action in (get_build, get_package, user_tasks):
        m = action.match(message)
        if m:
            return (action, m)


@match(match_koji)
def helga_koji(client, channel, nick, message, action_and_match):
    """
    Match information related to Koji.
    """
    profile = 'brew'  # todo: make this configurable
    koji = Connection(profile)

    d = defer.succeed(koji)
    (action, match) = action_and_match
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
