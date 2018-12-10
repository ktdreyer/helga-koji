from helga_koji import colors


def task_state(state_name):
    """
    A string like "free", "open", "closed"
    """
    name = state_name.lower()
    if name == 'free':
        return colors.purple(state_name)
    if name == 'open':
        return colors.orange(state_name)
    if name == 'closed':
        return colors.green(state_name)
    if name == 'canceled':
        return colors.brown(state_name)
    # if name == 'assigned':
    #     return colors.???(state_name)
    if name == 'failed':
        return colors.red(state_name)
    return state_name


def build_state(state_name):
    """
    A string like "building", "complete", "deleted", "failed", "canceled"
    """
    name = state_name.lower()
    if name == 'building':
        return colors.blue(state_name)
    if name == 'complete':
        return colors.green(state_name)
    if name == 'deleted':
        return colors.brown(state_name)
    if name == 'failed':
        return colors.red(state_name)
    if name == 'canceled':
        return colors.orange(state_name)
    return state_name
