from interfaces import IMapper
from zope.interface.declarations import _normalizeargs

from uuid import uuid1

from ore.alchemist import Session

def create(spec):
    # set up mapper
    mapper = IMapper(spec)

    # create instance
    instance = mapper()

    # set soup attributes
    instance.uuid = uuid1().hex
    instance.spec = mapper.__spec__

    # save to session
    session = Session()
    session.save(instance)

    return instance
