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
    return '%d min %2d secs' % (minutes, seconds)
