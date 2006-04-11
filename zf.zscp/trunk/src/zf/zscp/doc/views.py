
##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Certification

$Id$
"""
__docformat__ = "reStructuredText"


import os.path

from zope.app.renderer.rest import ReStructuredTextToHTMLRenderer
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserPublisher


class ReSt2HTMLView(object):
    """view implementation for SeleniumRegistry ."""
    
    implements(IBrowserPublisher)
    
    def __init__(self, context, request):
        
        self.context = context
        self.request = request

    def getRest2HTML(self):
        
        filename = unicode(os.path.join(os.path.dirname(__file__), '..', 'ProcessAndRepository.txt'))
        source = unicode(open(filename , 'rb').read())
        return ReStructuredTextToHTMLRenderer(source, self.request).render().strip()

        

