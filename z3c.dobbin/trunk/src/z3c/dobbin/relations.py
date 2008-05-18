from zope import interface

from interfaces import IMapper
from interfaces import IMapped

from session import getTransactionManager

from zope.dottedname.resolve import resolve
from ore.alchemist import Session

import factory
import bootstrap

def lookup(uuid, ignore_cache=False):
    session = Session()
    item = session.query(bootstrap.Soup).select_by(uuid=uuid)[0]

    # try to acquire relation target from session
    if not ignore_cache:
        try:
            return session._d_pending[item.uuid]
        except (AttributeError, KeyError):
            pass

    # build item
    return build(item.spec, item.uuid)

def build(spec, uuid):
    kls = resolve(spec)
    mapper = IMapper(kls)
    
    session = Session()
    return session.query(mapper).select_by(uuid=uuid)[0]

def persist(item):
    # create instance
    instance = factory.create(item.__class__)

    # assign uuid to item
    item._d_uuid = instance.uuid

    # hook into transaction
    try:
        manager = item._d_manager
    except AttributeError:
        manager = item._d_manager = getTransactionManager(item)
        
    manager.register()

    # update attributes
    update(instance, item)

    return instance

def update(instance, item):
    # set attributes
    for iface in interface.providedBy(item):
        for name in iface.names():
            value = getattr(item, name)
            setattr(instance, name, value)

