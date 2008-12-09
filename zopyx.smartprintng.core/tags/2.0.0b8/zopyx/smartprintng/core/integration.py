##########################################################################
# zopyx.smartprintng.core - High-quality export of Zope content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


"""
Convenience methods for 3rd-party integration 
"""

import zope.component

from interfaces import IHTMLExtractor, IHTMLTransformation
from resources import getResourcesFor


def availableTransformations():
    """ Returns a list of dicts representing the available HTML
        transformations. The 'name' key of the dict can be used to lookup
        the factory of the transformation. The 'description' gives
        a textual description of the transformation.
    """

    result = list()
    for name, cls in zope.component.getUtilitiesFor(IHTMLTransformation):
        result.append(dict(name=name,
                           description=cls.description))
    return result


def availableAggregators(context):
    """ Return a list of names of all registered IHTMLExtractor adapters for
        the current context object.
    """

    result = list()
    for name, adapter in zope.component.getAdapters((context,), IHTMLExtractor):
        result.append(dict(name=name,
                          ))
    return result

if __name__ == '__main__':
    import transformation
    print availableTransformations()
    print availableAggregators(None)
