
##########################################################################
# zopyx.smartprintng.core - High-quality export of Zope content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import zope.component
from interfaces import IHTMLExtractor
from zope.component import getAdapter
from zope.component.interfaces import ComponentLookupError


def aggregateHTML(context, adapter_name=''):
    """ Check if there is a registered html extractor adapter
        available. If yes, obtain the HTML to be rendered for the 
        given object through its adapter.
    """
    
    try:
        extractor = getAdapter(context, IHTMLExtractor, name=adapter_name)
        return extractor.getHTML()
    except ComponentLookupError:
        return None
