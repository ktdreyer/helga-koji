from twisted.internet import defer
from txkoji.connection import Connection
from txkoji.build import Build
from txkoji.task import Task
from txkoji.package import Package
import txkoji.build_states
from helga_koji.util import describe_delta
from helga_koji.util import describe_task
from datetime import datetime


def match(message):
    """
    "https://koji.example.com/koji/taskinfo?taskID=15741633"

    :returns: a txkoji.Connection instance if we matched, or None if not.
    """
    url = message.strip()
    conn = Connection.connect_from_web(url)
    if conn:
        return (conn, url)


@defer.inlineCallbacks
def describe_kojiweb(koji, conn_and_url, client, channel, nick):
    """
    Describe a resource from a kojiweb URL in a message
    """
    (conn, url) = conn_and_url
    resource = yield conn.from_web(url)

    if isinstance(resource, Build):
        msg = yield describe_build(resource)
    elif isinstance(resource, Task):
        desc = describe_task(resource)
        msg = 'that is a %s task' % desc
    elif isinstance(resource, Package):
        # print ongoing builds for this package?
        tmpl = 'that is the {package} package'
        msg = tmpl.format(package=resource.package)
    elif hasattr(resource, 'name'):
        tmpl = 'that is {name}'
        msg = tmpl.format(name=resource.name)
    else:
        msg = 'I could not process that Koji URL'
    if channel != nick:
        msg = '%s, %s' % (nick, msg)
    defer.returnValue(msg)


@defer.inlineCallbacks
def describe_build(build):
    """
    Describe a build: how long it's going to take
    """
    if build.state == txkoji.build_states.BUILDING:
        est_complete = yield build.estimate_completion()
        remaining = est_complete - datetime.utcnow()
        if remaining.total_seconds() > 0:
            tmpl = 'that {nvr} should finish building in {delta_text}'
            delta_text = describe_delta(remaining)
            msg = tmpl.format(nvr=build.nvr, delta_text=delta_text)
            defer.returnValue(msg)
        tmpl = 'that {nvr} exceeds estimate by {delta_text}'
        tmpl += ' (total time so far: %s)' % describe_delta(build.duration)
        delta_text = describe_delta(remaining)
        msg = tmpl.format(nvr=build.nvr, delta_text=delta_text)
        defer.returnValue(msg)
    # TODO: print the text of the build.state here as well.
    tmpl = 'that {nvr} build duration was {delta_text}'
    delta_text = describe_delta(build.duration)
    msg = tmpl.format(nvr=build.nvr, delta_text=delta_text)
    defer.returnValue(msg)


def send_message(message, shortname, client, channel, nick):
    """
    Send a message to channel.
    """
    if message:
        client.msg(channel, message)


# List of callbacks to fire on a match:
callbacks = (describe_kojiweb, send_message)
