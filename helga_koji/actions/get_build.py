from datetime import datetime
import re
from twisted.internet import defer
import txkoji.build_states
from helga_koji.util import describe_delta


class BuildMatch(object):
    def __init__(self, which, package):
        self.which = which
        self.package = package


def match(message):
    """
    "last ceph build"
    "current ceph build"

    :returns: a BuildMatch if we matched, or None if no match.
    """
    pattern = re.compile('^(last|current) (\S+) build\??$')
    m = re.match(pattern, message)
    if not m:
        return
    which_build = m.group(1)  # "last" or "current"
    package = m.group(2)  # eg. "ceph"
    build_match = BuildMatch(which_build, package)
    return build_match


@defer.inlineCallbacks
def describe_build(koji, build_match, client, channel, nick):
    """
    Describe this build's times in a message.
    """
    package = build_match.package
    state = txkoji.build_states.COMPLETE
    # note "order: -build_id" will list the newest (build timestamp) first.
    opts = {'limit': 1, 'order': '-build_id'}
    if build_match.which == 'current':
        state = txkoji.build_states.BUILDING
        opts = {'order': '-build_id'}
    builds = yield koji.listBuilds(package, state=state, queryOpts=opts)
    if not builds and build_match.which == 'current':
        msg = '{nick}, I could not find a running {package} build. ' \
              'Try searching "last {package} build" to find completed ' \
              'builds?'.format(nick=nick, package=package)
        defer.returnValue(msg)
    if not builds and build_match.which == 'last':
        # Maybe a brand new package
        tmpl = '{nick}, I could find no completed builds for {package}.'
        msg = tmpl.format(nick=nick, package=package)
        defer.returnValue(msg)
    if len(builds) > 1:
        # In theory we could handle printing multiple builds, but for now this
        # is rare so I'm not implementing it.
        pkg = yield koji.getPackage(package)
        tmpl = '{nick}, {num} {package} builds running at the moment: {url}'
        msg = tmpl.format(nick=nick, num=len(builds), package=package,
                          url=pkg.url)
        defer.returnValue(msg)
    build = builds[0]
    if build_match.which == 'current':
        # TODO: if we catch txkoji's NoDescendentsError here, it means there's
        # no way to estimate the build yet. Just link to the task.
        est_complete = yield build.estimate_completion()
        remaining = est_complete - datetime.utcnow()
        if remaining.total_seconds() > 0:
            tmpl = '{nick}, {nvr} should finish building in {delta_text} {url}'
            delta_text = describe_delta(remaining)
        else:
            tmpl = '{nick}, {nvr} exceeds estimate by {delta_text} {url}'
            tmpl += ' (total time so far: %s)' % describe_delta(build.duration)
            delta_text = describe_delta(remaining)
    else:
        tmpl = '{nick}, {nvr} build duration was {delta_text} {url}'
        delta_text = describe_delta(build.duration)
    msg = tmpl.format(nick=nick, nvr=build.nvr, delta_text=delta_text,
                      url=build.url)
    defer.returnValue(msg)


def send_message(message, shortname, client, channel, nick):
    """
    Send a message to channel.
    """
    if message:
        client.msg(channel, message)


# List of callbacks to fire on a match:
callbacks = (describe_build, send_message)
