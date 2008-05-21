from interfaces import IMapper
from zope.interface.declarations import _normalizeargs

from uuid import uuid1
from random import randint

from ore.alchemist import Session

def uuid():
    """Return new unique id as string.

    Force first character between 'a' and 'z'.
    """
    
    return chr(randint(ord('a'), ord('z'))) + uuid1().hex[:-1]

def create(spec):
    # set up mapper
    mapper = IMapper(spec)

    # create instance
    instance = mapper()

    # set soup attributes
    instance.uuid = uuid()
    instance.spec = mapper.__spec__

    # save to session
    session = Session()
    session.save(instance)

    return instance
