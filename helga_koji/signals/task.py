import json
import smokesignal
from twisted.internet import defer
from twisted.python.compat import StringType
from txkoji.task import Task
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
    task = from_umb_frame(frame)

    yield util.populate_owner_name(task)
    owner_name = util.shorten_fqdn(task.owner_name)
    task.tag_name = yield get_tag_name(task)
    description = get_description(task)
    state_name = task.event

    if not is_interesting(task):
        defer.returnValue(None)

    mtmpl = "{owner_name}'s {description} task {state} ({url})"
    message = mtmpl.format(owner_name=owner_name,
                           description=description,
                           state=state_name,
                           url=task.url)
    if task.tag_name:
        product = util.product_from_name(task.tag_name)
    elif task.target:
        product = util.product_from_name(task.target)
    else:
        logger.warn('found no tag nor target name for task %d' % task.id)
        product = ''
    defer.returnValue((message, product))


def is_interesting(task):
    if getattr(task, 'owner_name') in ('kojira', 'mbs'):
        return False
    if task.method in SKIP_METHODS:
        return False
    if task.owner_name == 'tdawson' \
       and task.is_scratch \
       and task.target.startswith('rhel-8.0'):
        # skip rhel-8 scratch builds
        return False
    return True


def from_umb_frame(frame):
    data = json.loads(frame.body)
    info = data['info']
    task = Task.fromDict(info)
    task.connection = util.koji
    task.event = data['new']
    return task


def get_description(task):
    """ Textual description for this task's method and attributes. """
    desc = task.method
    if task.is_scratch:
        desc = 'scratch %s' % desc
    if task.package:
        desc = '%s %s' % (task.package, desc)
    if task.target:
        desc += ' for %s' % task.target
    if task.arch:
        desc += ' for %s' % task.arch
    if task.tag_name:
        desc += ' for tag %s' % task.tag_name
    return desc


@defer.inlineCallbacks
def get_tag_name(task):
    """
    Return the name of the tag of this task.

    :returns: str, or None if there is no tag for this task.
    """
    name_or_id = yield defer.succeed(task.tag)
    if name_or_id is None:
        defer.returnValue(None)
    if isinstance(name_or_id, StringType):
        defer.returnValue(name_or_id)
    if isinstance(name_or_id, int):
        name = yield task.connection.cache.tag_name(name_or_id)
        defer.returnValue(name)
