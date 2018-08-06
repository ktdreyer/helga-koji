import smokesignal
from twisted.internet import defer
from txkoji.messages import BuildStateChange
from txkoji.messages import TagUntag
from helga_koji import colors
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
    """
    event = BuildStateChange.from_frame(frame, util.koji)

    user = yield event.user()
    user = util.shorten_fqdn(user)

    state = event.event.lower()
    state = colorize(state)

    mtmpl = "{user}'s {nvr} {state} ({url})"
    message = mtmpl.format(user=user,
                           nvr=event.build.nvr,
                           state=state,
                           url=event.url)
    product = yield get_product(event)
    defer.returnValue((message, product))


@smokesignal.on('umb.eng.brew.build.tag')
@smokesignal.on('umb.eng.brew.build.untag')
@defer.inlineCallbacks
def build_tag_untag(frame):
    """
    Process a "Tag"/"Untag" message.
    """
    event = TagUntag.from_frame(frame, util.koji)

    user = yield event.user()
    user = util.shorten_fqdn(user)

    action = event.event.lower()
    if action == 'tag':
        mtmpl = "{user} tagged {nvr} into {tag}"
    if action == 'untag':
        mtmpl = "{user} untagged {nvr} from {tag}"

    message = mtmpl.format(user=user,
                           nvr=event.build.nvr,
                           tag=event.tag)
    product = util.product_from_name(event.tag)
    defer.returnValue((message, product))


@defer.inlineCallbacks
def get_product(event):
    """
    Return a "product" string for this build.

    Try locating the build's task/target name first, and falling back to the
    build's first tag's name.

    :returns: deferred that when fired returns the build "product" string, or
              an empty string if no product could be determined.
    """
    build = event.build
    target = yield build.target()
    if target:
        product = util.product_from_name(target)
        defer.returnValue(product)
    tags = yield tag_names(build)
    if tags:
        if len(tags) > 1:
            # Are the other ones relevant?
            logger.warning('%s has multiple tags: %s' % (build.url, tags))
        product = util.product_from_name(tags[0])
        defer.returnValue(product)
    logger.error('found no tag nor target name for %s %s'
                 % (event.build.state, event.build.url))
    defer.returnValue('')


@defer.inlineCallbacks
def tag_names(build):
    """
    Find the names of the tags for this build.

    :returns: deferred that when fired returns a (possibly-empty) list of tag
              names.
    """
    tags = yield build.tags()
    names = [tag.name for tag in tags]
    defer.returnValue(names)


def colorize(state):
    """
    A string like "building", "complete", "deleted", "failed", "canceled"
    """
    if state == 'building':
        return colors.blue(state)
    if state == 'complete':
        return colors.green(state)
    if state == 'deleted':
        return colors.brown(state)
    if state == 'failed':
        return colors.red(state)
    if state == 'canceled':
        return colors.orange(state)
    return state
