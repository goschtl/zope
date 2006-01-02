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
"""

$Id: wikilink.py 38895 2005-10-07 15:09:36Z dominikhuber $
"""
__docformat__ = 'restructuredtext'

import re

from zope.interface import implements
from zope.component import adapts

from zorg.wikification.parser import BaseHTMLProcessor
from zorg.wikification.browser.interfaces import IWikiPage
from zorg.wikification.browser.interfaces import ILinkProcessor


class BaseLinkProcessor(BaseHTMLProcessor) :
    """ A link processor that wikifies the links by modifying the
        href of a link.
    """
    
    implements(ILinkProcessor)
    adapts(IWikiPage)
    
    def __init__(self, caller) :
        BaseHTMLProcessor.__init__(self)
        self.caller = caller
              
    def update_link(self, attrs) :
        """ Mark link css. """
        result = []
        _class = False
        for key, value in attrs :
            if key == "class" :
                value += " wiki-link"
                _class = True
            result.append((key, value))
        if not _class :
            result.append(("class", "wiki-link"))
        return result
                            
    def unknown_starttag(self, tag, attrs):
        if tag == "a" :
            new = False
            modified = []
            for key, value in attrs :
                if key == "href" :
                    new, value = self.caller.wikifyLink(value)
                modified.append((key, value))
            if new :
                result = self.update_link(modified)
                BaseHTMLProcessor.unknown_starttag(self, tag, result)
                return True
        BaseHTMLProcessor.unknown_starttag(self, tag, attrs)               

    def handle_data(self, text):
        # called for each block of plain text, i.e. outside of any tag and
        # not containing any character or entity references
        
        text_link = re.compile('\[.*?\]', re.VERBOSE)
        
        result = ""
        end = 0
        for m in text_link.finditer(text):
            
            start = m.start()
            end = m.end()
            result += text[end:start]
            between = text[start+1:end-1]
            result += self.caller.wikifyTextLink(between)
            
        result += text[end:]
        self.pieces.append(result)


class JavaScriptLinkProcessor(BaseLinkProcessor) :
    """ A link processor that wikifies the links by modifying the
        href of a link and additionally inserting a javascript function
        that allows the user to choose an edit option. 
    """
    
    javascript = "wikiOptions();"
    
    def update_link(self, attrs) :
        """ Adds a onclick handler to the link. """
        result = super(JavaScriptLinkProcessor, self).update_link()
        result.append("onclick", self.javascript)
        return result
        
    
    