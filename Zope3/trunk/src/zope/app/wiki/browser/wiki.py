##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser View Components for Wikis

$Id: wiki.py,v 1.2 2004/03/01 15:02:54 philikon Exp $
"""
from datetime import datetime
from zope.proxy import removeAllProxies

from zope.app import zapi
from zope.app.dublincore.interfaces import ICMFDublinCore
from zope.app.services.servicenames import HubIds
from zope.app.traversing import getName, getPath
from zope.app.browser.container.adding import Adding
from zope.app.services.hub import Registration

from zope.app.wiki.interfaces import IWikiPageHierarchy
from zope.app.wiki.index import WikiTextIndex

class WikiAdding(Adding):
    """Custom adding view for NewsSite objects."""
    menu_id = "add_wiki"


class AddWiki(object):
    """Add a Wiki"""

    def createAndAdd(self, data):
        content = super(AddWiki, self).createAndAdd(data)
        if self.request.get('textindex'):
            # Get the environment
            sm = zapi.getServiceManager(content)
            pkg = sm['default']
            hub = pkg['HubIds-1']
            # Create, subscribe and add a Registration object.
            if 'WikiReg' not in pkg: 
                reg = Registration()
                pkg['WikiReg'] = reg
                reg.subscribe()
            # Create, subscribe and add an WikiTextIndex object
            if 'WikiTextIndex' not in pkg: 
                index = WikiTextIndex()
                pkg['WikiTextIndex'] = index
                index.subscribe(hub, True)

        if self.request.get('frontpage'):
            page = removeAllProxies(zapi.createObject(None, 'WikiPage'))
            page.type = u'reStructured Text (reST)'
            page.source = u'This is the FrontPage of the Wiki.'
            dc = zapi.getAdapter(page, ICMFDublinCore)
            dc.created = datetime.now()
            dc.modified = datetime.now()
            dc.creators = [u'wiki']
            content['FrontPage'] = page

        return content


class WikiSearch(object):
    """Search Wiki Pages"""

    def __init__(self, context, request):
        super(WikiSearch, self).__init__(context, request)
        self.hub = zapi.getService(context, HubIds)

    def query(self):
        queryText = self.request.get('queryText', '')
        sm = zapi.getServiceManager(self.context)
        results, total = sm['default']['WikiTextIndex'].query(queryText)
        result = {
            'results': list(self._resultIterator(results)),
            'total': total,
            }
        return result
    
    def _resultIterator(self, results):
        for hubid, score in results:
            yield self._cookInfo(hubid, score)

    def _cookInfo(self, hubid, score):
        location = self.hub.getPath(hubid)
        scoreLabel = "%.1f%%" % (100.0 * score)
        result = {
            'location': location,
            'score': score,
            'scoreLabel': scoreLabel,
            }
        try:
            object = self.hub.getObject(hubid)
        except NotFoundError:
            pass
        else:
            result['name'] = getName(object)
        return result


class TableOfContents:
    """Table of contents for a Wiki"""

    def toc(self):
        """Generate a table of contents."""
        children = []

        for name, page in self.context.items():
            hier = zapi.getAdapter(page, IWikiPageHierarchy)
            if hier.getParents() == ():
                children.append((page, hier.findChildren())) 
        return self._branchHTML(children)

    def _branchHTML(self, children):
        html = '<ul>\n'
        for child, subs in children:
            html += ' <li><a href="%s">%s</a></li>\n' %(getName(child),
                                                        getName(child))
            if subs:
                html += self._branchHTML(subs)
        html += '</ul>\n'
        return html
