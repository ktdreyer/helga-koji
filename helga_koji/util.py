def describe_delta(delta):
    """
    Describe this timedelta in human-readable terms.
    :param delta: datetime.timedelta object
    :returns: str, describing this delta
    """
    s = delta.total_seconds()
    s = abs(s)
    hours, remainder = divmod(s, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return '%d hr %d min' % (hours, minutes)
    if minutes:
        return '%d min %d secs' % (minutes, seconds)
    return '%d secs' % seconds


def describe_task(task):
    """ Describe this task in human-readable terms.

    :param task: txkoji.task.Task object
    :returns: str, describing this task
    """
    desc = task.method
    if task.is_scratch:
        desc = 'scratch %s' % desc
    if task.package:
        desc = '%s %s' % (task.package, desc)
    if task.target:
        desc += ' for %s' % task.target
    if task.arch:
        desc += ' for %s' % task.arch
    return desc
