from interfaces import IMapper
from zope.interface.declarations import _normalizeargs

from ore.alchemist import Session

def create(spec):
    # set up mapper
    mapper = IMapper(spec)

    # create instance
    return mapper()
