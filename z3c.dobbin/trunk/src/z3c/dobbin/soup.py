from zope import interface

from interfaces import IMapper
from interfaces import IMapped

from session import registerObject

from zope.dottedname.resolve import resolve
from ore.alchemist import Session

import factory
import bootstrap
import interfaces
import types

BASIC_TYPES = (int, float, str, unicode, tuple, list, set, dict)

IMMUTABLE_TYPES = (int, float, str, unicode, tuple)
    
def lookup(uuid, ignore_pending=False):
    session = Session()

    # check if object is in pending session objects
    if not ignore_pending:
        try:
            return session._d_pending[uuid]
        except (AttributeError, KeyError):
            pass

    try:
        item = session.query(bootstrap.Soup).filter_by(uuid=uuid)[0]
    except IndexError:
        raise LookupError("Unable to locate object with UUID = '%s'." % uuid)
        
    # build item
    return build(item.spec, item.uuid)

def build(spec, uuid):
    kls = resolve(spec)
    mapper = IMapper(kls)
    
    session = Session()
    return session.query(mapper).filter_by(uuid=uuid)[0]

def persist(item):
    instance = interfaces.IMapped(item)

    if interfaces.IBasicType.providedBy(instance):
        instance.value = item
    else:
        update(instance, item)

    # set soup identifier on instances
    if type(item) not in BASIC_TYPES:
        item._d_uuid = instance.uuid

    # register mutable objects with transaction manager
    if type(item) not in IMMUTABLE_TYPES:
        registerObject(item, instance.uuid)
                        
    return instance

def update(instance, item):
    # set attributes
    for iface in interface.providedBy(item):
        for name in iface.names():
            value = getattr(item, name)
            setattr(instance, name, value)

