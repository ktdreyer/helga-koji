from datetime import datetime
from twisted.internet import defer
from helga_koji import colorize
from txkoji.task import NoDescendentsError


def describe_delta(delta):
    """
    Describe this timedelta in human-readable terms.
    :param delta: datetime.timedelta object
    :returns: str, describing this delta
    """
    s = delta.total_seconds()
    s = abs(s)
    days, remainder = divmod(s, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    if days:
        return '%d d %d hr' % (days, hours)
    if hours:
        return '%d hr %d min' % (hours, minutes)
    if minutes:
        return '%d min %d secs' % (minutes, seconds)
    return '%d secs' % seconds


def describe_remaining(est_complete):
    """
    Describe this estimated completion time in human-readable terms.

    :param est_complete: datetime.datetime object
    :returns: str, describing this estimated completion time.
    """
    remaining = est_complete - datetime.utcnow()
    if remaining.total_seconds() > 0:
        return 'should be done in %s' % describe_delta(remaining)
    return 'exceeds estimate by %s' % describe_delta(remaining)


def describe_task_state(task, delta):
    """ Describe a task's state in human-readable terms.

    :param task: txkoji.task.Task object
    :returns: str describing this task's state.
    """
    state_name = task.state_name.lower()
    state_colorized = colorize.task_state(state_name)
    delta_text = describe_delta(delta)
    if state_name == 'closed':
        # use a term that's easier to understand
        state_colorized = state_colorized.replace('closed', 'completed')
        tmpl = '{state} in {delta}'
    if state_name == 'canceled' or state_name == 'failed':
        tmpl = '{state} {delta} into the build'
    return tmpl.format(state=state_colorized, delta=delta_text)


@defer.inlineCallbacks
def describe_task(task, user=None):
    """ Describe this task in human-readable terms.

    :param task: txkoji.task.Task object
    :param user: Koji user account name, if you know it.
    :returns: deferred that when fired returns a str, describing this task.
              "joeuser's llvm scratch build should be done in 1 hr 21 min"
    """
    tmpl = "{user}'s {description} {state}"
    if not user:
        user = yield task.connection.cache.user_name(task.owner)
    description = task.method
    if task.is_scratch:
        description = 'scratch %s' % description
    if task.package:
        description = '%s %s' % (task.package, description)
    if task.target:
        description += ' for %s' % task.target
    if task.arch:
        description += ' for %s' % task.arch
    if task.completed:
        state = describe_task_state(task, task.duration)
    else:
        try:
            est_complete = yield task.estimate_completion()
        except NoDescendentsError:
            est_complete = None
        if est_complete:
            state = describe_remaining(est_complete)
        elif task.duration:
            state = 'run time is %s' % describe_delta(task.duration)
        else:
            state_name = task.state_name.lower()
            state = 'in %s state' % colorize(state_name)
    result = tmpl.format(user=user, description=description, state=state)
    defer.returnValue(result)
