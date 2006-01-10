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
"""Multiadapter to handle the parsing of HTTP IF headers.

$Id$
"""
import re, urllib

from zope.interface import implements

from zope.app import zapi
from zope.app.container.interfaces import IReadContainer
from zope.app.locking.interfaces import ILockable

from interfaces import IIfHeader

### If: header handling support.  IfParser returns a sequence of
### TagList objects in the order they were parsed which can then
### be used in WebDAV methods to decide whether an operation can
### proceed or to raise HTTP Error 412 (Precondition failed)
ifheaderre = re.compile(
    r"(?P<resource><.+?>)?\s*\((?P<listitem>[^)]+)\)"
    )

listitemre = re.compile(
    r"(?P<not>not)?\s*(?P<listitem><[a-zA-Z]+:[^>]*>|\[.*?\])",
    re.I)

class TagList:
    def __init__(self):
        self.resource = None
        self.list = []
        self.notted = 0

class IfParser(object):
    """Note that I just ignore any etags passed in the IF header. This is
    because basically etags are not supported under Zope3 yet has far has I
    know.
    """
    implements(IIfHeader)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def ifParser(self, hdr):
        out = []
        i = 0
        while 1:
            m = ifheaderre.search(hdr[i:])
            if not m:
                break

            i = i + m.end()
            tag = TagList()
            tag.resource = m.group('resource')
            if tag.resource:                # We need to delete < >
                tag.resource = tag.resource[1:-1]
            listitem = m.group('listitem')
            tag.notted, tag.list = self.listParser(listitem)
            out.append(tag)

        return out

    def listParser(self, listitem):
        out = []
        notted = 0
        i = 0
        while 1:
            m = listitemre.search(listitem[i:])
            if not m:
                break

            i = i + m.end()
            out.append(m.group('listitem'))

            if m.group('not'):
                notted = 1

        return notted, out

    def tokenFinder(self, token):
        """return lock tokens
        """
        # takes a string like '<opaquelocktoken:afsdfadfadf> and returns the
        # token part.
        if not token:
            return None           # An empty string was passed in

        if token[0] == '[':
            return None     # An Etag was passed in

        if token[0] == '<':
            token = token[1:-1]

        ## return token[token.find(':') + 1:]
        return token

    def __call__(self):
        ifhdr = self.request.getHeader('if', None)
        if ifhdr is None:
            return True

        lockable = ILockable(self.context)
        if not lockable.locked():
            return True

        lockinfo = lockable.getLockInfo()

        tags = self.ifParser(ifhdr)

        resource_url = zapi.absoluteURL(self.context, self.request)
        if IReadContainer.providedBy(self.context):
            resource_url += '/'

        # found is a boolean indicated whether or not we have found the current
        # locktoken
        found = False
        # resourcetagged is a boolean indicating that the current context
        # has being referenced in the
        resourcetagged = False
        # resources is a boolean indicating that the if header has specified
        # some resources
        resources = False
        for tag in tags:
            if not tag.resource:
                # if resources is True then we have a problem with the logic of
                # this method - also I think this is against the rfc2518 proto
                token_list = map(self.tokenFinder, tag.list)
                wehavetokens = filter(
                    lambda token: token == lockinfo.get('lockuri', ''),
                    token_list)

                if not wehavetokens:
                    continue

                if tag.notted:
                    continue

                found = True
                break
            else:
                resources = True

                url = tag.resource
                if url[0] != '/':
                    type, url = urllib.splittype(url)
                    home, url = urllib.splithost(url)

                if resource_url == url:
                    resourcetagged = True

                    token_list = map(self.tokenFinder, tag.list)
                    wehavetoken = filter(
                        lambda token: token == lockinfo.get('lockuri', ''),
                        token_list)

                    if not wehavetoken:
                        continue

                    if tag.notted:
                        continue

                    found = True
                    break

        if found:
            return True
        if resources and not resourcetagged:
            return True
        return False
