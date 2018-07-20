import json
import smokesignal
from twisted.internet import defer
from txkoji.build import Build
from helga_koji.signals import util
from helga import log


logger = log.getLogger(__name__)


@smokesignal.on('umb.eng.brew.build.building')
@smokesignal.on('umb.eng.brew.build.canceled')
@smokesignal.on('umb.eng.brew.build.complete')
@smokesignal.on('umb.eng.brew.build.failed')
@defer.inlineCallbacks
def build_state_change_callback(frame):
    """
    Process a "BuildStateChange" message.

    Note we probably want to process brew.build.tag too, so we can skip all the
    tagBuild noise in the brew.task listener.
    """
    build = from_state_change_umb_frame(frame)

    yield util.populate_owner_name(build)
    owner_name = util.shorten_fqdn(build.owner_name)

    mtmpl = "{owner_name}'s {nvr} {event} ({build_url})"
    message = mtmpl.format(owner_name=owner_name,
                           nvr=build.nvr,
                           event=build.event,
                           build_url=build.url)
    product = yield get_product(build)
    defer.returnValue((message, product))


def from_state_change_umb_frame(frame):
    dest = frame.headers['destination']
    (_, event) = dest.rsplit('.', 1)
    data = json.loads(frame.body)
    info = data['info']
    build = Build.fromDict(info)
    build.connection = util.koji
    build.event = event
    return build


@defer.inlineCallbacks
def get_product(build):
    """
    Return a "product" string for this build.

    Try locating the build's task/target name first, and falling back to the
    build's first tag's name.

    :returns: deferred that when fired returns the build "product" string, or
              an empty string if no product could be determined.
    """
    target = yield get_target(build)
    if target:
        product = util.product_from_name(target)
        defer.returnValue(product)
    tags = yield get_tags(build)
    if tags:
        if len(tags) > 1:
            # Are the other ones relevant?
            logger.warning('%s has multiple tags: %s' % (build.url, tags))
        product = util.product_from_name(tags[0])
        defer.returnValue(product)
    logger.error('found no tags or target name for %s' % build.url)
    logger.error(build.params)  # debugging
    defer.returnValue('')


@defer.inlineCallbacks
def get_target(build):
    """
    Find the name of this build's target.

    :returns: deferred that when fired returns the build's task's target name,
              or None if we could not find it.
    """
    task = yield build.task()
    if not task:
        logger.debug('no task found for %s' % build.url)
        yield defer.succeed(None)
        defer.returnValue(None)
    defer.returnValue(task.target)


@defer.inlineCallbacks
def get_tags(build):
    """
    Find the names of the tags for this build.

    :returns: deferred that when fired returns a (possibly-empty) list of tag
              names.
    """
    tags = yield build.tags()
    names = [tag.name for tag in tags]
    defer.returnValue(names)
