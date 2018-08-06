from twisted.internet import defer
from twisted.python.compat import StringType
from txkoji import Connection


# We currently only support parsing Brew's UMB messages.
koji = Connection('brew')


@defer.inlineCallbacks
def populate_owner_name(instance):
    """
    Assign an .owner_name to this task or build, using caching.

    :param instance: txkoji.Task or txkoji.Build instance
    """
    # Not every message has an owner_name, see BREW-1640
    # In fact tasks do *not*, so we should do this elsewhere.
    if hasattr(instance, 'owner_name'):
        defer.returnValue(None)
    if isinstance(instance.owner, StringType):
        instance.owner_name = instance.owner
        defer.returnValue(None)
    owner_id = getattr(instance, 'owner_id', instance.owner)
    name = yield instance.connection.cache.user_name(owner_id)
    instance.owner_name = name
    defer.returnValue(None)


def shorten_fqdn(name):
    """ Shorten any system account FQDN for readability. """
    if '.' in name:
        (name, _) = name.split('.', 1)
    return name


def product_from_name(name):
    """
    Return a product name from this tag name or target name.

    :param name: eg. "ceph-3.0-rhel-7"
    :returns: eg. "ceph"
    """
    if name.startswith('guest-'):
        # deal with eg. "guest-rhel-X.0-image"
        name = name[6:]
    parts = name.split('-', 1)
    return parts[0]
