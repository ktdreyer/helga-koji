from datetime import datetime
import posixpath
import re
from twisted.internet import defer
from txkoji import task_states
from txkoji.task import NoDescendentsError
from helga_koji.util import describe_delta


class TaskMatch(object):
    """ Match Koji tasks for a given *user* and *state* """
    def __init__(self, user, state):
        self.user = user
        self.state = state

    @classmethod
    def from_text(klass, text):
        parts = re.split('\s+', text)
        user = parts[0]
        if len(parts) == 1:
            state = 'open'  # default to open ;)
        elif len(parts) == 2:
            state = parts[1]
        else:
            return None  # could not parse this text
        # cleanup a possessive username
        if user.endswith("'s"):
            user = user[:-2]
        if user.endswith("'"):
            user = user[:-1]
        return klass(user, state)


def match(message):
    """
    "kdreyer's tasks"
    "kdreyer's task"
    "kdreyer tasks"

    :returns: a TaskMatch if we matched, or None if not.
    """
    pattern = re.compile("(.+) tasks?\??$")
    m = re.match(pattern, message)
    if not m:
        return
    task_text = m.group(1)  # "kdreyer" or "kdreyer's" or "kdreyer's open"
    return TaskMatch.from_text(task_text)


@defer.inlineCallbacks
def describe_tasks(koji, task_match, client, channel, nick):
    """
    Describe this user's tasks in a message
    """
    state_name = task_match.state.upper()
    try:
        state = getattr(task_states, state_name)
    except AttributeError:
        tmpl = '{nick}, I do not know about {state} tasks.'
        msg = tmpl.format(nick=nick, state=state_name)
        defer.returnValue(msg)
    owner = yield koji.getUser(task_match.user)
    if not owner:
        tmpl = '{nick}, I could not find a koji user account for {user}'
        msg = tmpl.format(nick=nick, user=task_match.user)
        defer.returnValue(msg)
    opts = {'state': [state], 'owner': owner.id}
    qopts = {'order': 'priority,create_time'}
    tasks = yield koji.listTasks(opts, qopts)

    # Filter out the child tasks. We don't need to be that literal here.
    child_methods = ('buildArch', 'buildSRPMFromSCM', 'createrepo')
    tasks = [t for t in tasks if t.method not in child_methods]
    if not tasks:
        msg = describe_no_tasks(nick, task_match)
        defer.returnValue(msg)
    if len(tasks) == 1:
        task = tasks[0]
        est_complete = None
        if task.method == 'build' and task.state == task_states.OPEN:
            try:
                est_complete = yield task.estimate_completion()
            except NoDescendentsError:
                # we cannot determine an est_complete value because the
                # buildArch tasks haven't begun yet.
                pass
        msg = describe_one_task(nick, task, task_match, est_complete)
        defer.returnValue(msg)
    msg = describe_multiple_tasks(nick, tasks, task_match)
    defer.returnValue(msg)


def describe_no_tasks(nick, task_match):
    """ No tasks matched """
    tmpl = '{nick}, I could not find {state} tasks for {user}.'
    msg = tmpl.format(nick=nick, state=task_match.state, user=task_match.user)
    return msg


def describe_one_task(nick, task, task_match, est_complete=None):
    tmpl = "{nick}, {user}'s {package} {method} {duration} ({url})"
    method = task.method
    if task.is_scratch:
        method = 'scratch %s' % method
    if est_complete:
        remaining = est_complete - datetime.utcnow()
        if remaining.total_seconds() > 0:
            duration = 'should be done in %s' % describe_delta(remaining)
        else:
            duration = 'exceeds estimate by %s' % describe_delta(remaining)
    else:
        if task.state in (task_states.FREE, task_states.OPEN):
            duration_tmpl = 'run time is %s'
        else:
            duration_tmpl = 'run time was %s'
        duration = duration_tmpl % describe_delta(task.duration)
    msg = tmpl.format(nick=nick,
                      user=task_match.user,
                      package=task.package,
                      method=method,
                      duration=duration,
                      url=task.url)
    return msg


def describe_multiple_tasks(nick, tasks, task_match):
    # Multiple tasks matched
    urltmpl = 'tasks?owner={user}&state={state}&view=tree&order=-id'
    endpoint = urltmpl.format(user=task_match.user, state=task_match.state)
    url = posixpath.join(tasks[0].connection.weburl, endpoint)
    tmpl = '{nick}, {user} has {num} {state} tasks {url}'
    msg = tmpl.format(nick=nick,
                      user=task_match.user,
                      num=len(tasks),
                      state=task_match.state,
                      url=url)
    return msg


def send_message(message, shortname, client, channel, nick):
    """
    Send a message to channel.
    """
    if message:
        client.msg(channel, message)


# List of callbacks to fire on a match:
callbacks = (describe_tasks, send_message)
