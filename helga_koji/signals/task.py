import smokesignal
from twisted.internet import defer
from txkoji.messages import TaskStateChange
from helga_koji import colors
from helga_koji.signals import util
from helga import log


logger = log.getLogger(__name__)

SKIP_METHODS = ('build-fullsource',
                'buildArch',
                'buildFullSRPMFromSCM',  # ie. kernel
                'buildNotification',
                'buildSRPMFromSCM',
                'createdistrepo',
                'createLiveCD',
                'createrepo',
                'tagNotification',
                'vmExec',
                'winbuild',
                )


@smokesignal.on('umb.eng.brew.task.assigned')
@smokesignal.on('umb.eng.brew.task.canceled')
@smokesignal.on('umb.eng.brew.task.closed')
@smokesignal.on('umb.eng.brew.task.free')
@smokesignal.on('umb.eng.brew.task.failed')
@smokesignal.on('umb.eng.brew.task.free')
@smokesignal.on('umb.eng.brew.task.open')
@defer.inlineCallbacks
def task_state_change(frame):
    """ Process a "TaskStateChange" message. """
    event = TaskStateChange.from_frame(frame, util.koji)

    user = yield event.user()
    user = util.shorten_fqdn(user)

    tag_name = yield event.tag()

    if not is_interesting(event.task, user):
        defer.returnValue(None)

    description = describe_event(event, tag_name)

    event_text = event.event.lower()  # "free", "open", "closed"
    event_text = colorize(event_text)

    mtmpl = "{user}'s {description} task {event_text} ({url})"
    message = mtmpl.format(user=user,
                           description=description,
                           event_text=event_text,
                           url=event.url)
    if tag_name:
        product = util.product_from_name(tag_name)
    elif event.task.target:
        product = util.product_from_name(event.task.target)
    else:
        logger.warn('found no tag nor target name for task %d %s'
                    % (event.task.id, event.task.state))
        product = ''
    defer.returnValue((message, product))


def is_interesting(task, user):
    if user in ('kojira', 'mbs'):
        return False
    if task.method in SKIP_METHODS:
        return False
    if user == 'tdawson' \
       and task.is_scratch \
       and task.target.startswith('rhel-8.0'):
        # skip rhel-8 scratch builds
        return False
    return True


def describe_event(event, tag):
    """ Textual description for this task's method and attributes. """
    task = event.task
    desc = task.method
    if task.is_scratch:
        desc = 'scratch %s' % desc
    if task.package:
        desc = '%s %s' % (task.package, desc)
    if task.target:
        desc += ' for %s' % task.target
    if task.arch:
        desc += ' for %s' % task.arch
    if tag:
        desc += ' for tag %s' % tag
    return desc


def colorize(event_text):
    """
    A string like "free", "open", "closed"
    """
    if event_text == 'free':
        return colors.purple(event_text)
    if event_text == 'open':
        return colors.orange(event_text)
    if event_text == 'closed':
        return colors.green(event_text)
    if event_text == 'canceled':
        return colors.brown(event_text)
    # if event_text == 'assigned':
    #     return colors.???(event_text)
    if event_text == 'failed':
        return colors.red(event_text)
    return event_text
