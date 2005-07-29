##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Browser View Components for WikiPages

$Id$
"""
import re
from urllib import quote

from zope.proxy import removeAllProxies
from zope.app.publisher.browser import BrowserView

from zope.app import zapi
from zope.app.form.browser.submit import Update
from zope.app.dublincore.interfaces import ICMFDublinCore
from zope.app.traversing.api import getParent, getName

from zwiki.interfaces import IWikiPageHierarchy, IMailSubscriptions

urlchars = r'[A-Za-z0-9/:@_%~#=&\.\-\?\+\$,]+'
urlendchar  = r'[A-Za-z0-9/]'
url_re = r'["=]?((about|gopher|http|https|ftp|mailto|file):%s)' % urlchars
url = re.compile(url_re)

bracketedexpr_re = r'\[([^\n\]]+)\]'
bracketedexpr = re.compile(bracketedexpr_re)

protectedLine = re.compile(r'(?m)^!(.*)$')

U = 'A-Z\xc0-\xdf'
L = 'a-z\xe0-\xff'
b = '(?<![%s0-9])' % (U + L)
wikiname1 = r'(?L)%s[%s]+[%s]+[%s][%s]*[0-9]*' % (b, U, L, U, U + L)
wikiname2 = r'(?L)%s[%s][%s]+[%s][%s]*[0-9]*'  % (b, U, U, L, U + L)
wikilink  = re.compile(r'!?(%s|%s|%s|%s)' %
            (wikiname1, wikiname2, bracketedexpr_re, url_re))
localwikilink = r'!?(%s|%s|%s)' % (wikiname1, wikiname2, bracketedexpr_re)
interwikilink = re.compile(r'!?((?P<local>%s):(?P<remote>%s))' %
                (localwikilink, urlchars + urlendchar))


class DublinCoreViews(BrowserView):

    def author(self):
        """Get user who last modified the Wiki Page."""
        creators = ICMFDublinCore(self.context).creators
        if not creators:
            return 'unknown'
        return creators[0]

    def modified(self):
        """Get last modification date."""
        date = ICMFDublinCore(self.context).modified
        if date is None:
            date = ICMFDublinCore(self.context).created
        if date is None:
            return ''
        formatter = self.request.locale.dates.getFormatter('dateTime', 'medium')
        return formatter.format(date)


class GenericWikiPageViews(DublinCoreViews):
    """Some generic Wiki page views."""

    def breadcrumbs(self):
        """Get the path of this page."""
        hier = IWikiPageHierarchy(self.context)
        path = hier.path()
        html = []
        for page in path:
            html.append('<a href="../%s">%s</a>' %(getName(page),
                                                   getName(page)))
        return ' / '.join(html)

    def jumpTo(self, jumpto):
        """Try to get quickly to another Wiki page"""
        wiki = getParent(self.context)
        if jumpto in wiki:
            return self.request.response.redirect('../'+jumpto)
        else:
            return self.request.response.redirect('.')

    def toc(self):
        """Simply forwards to the real TOC in the Wiki."""
        return self.request.response.redirect('../@@toc.html')


class AddWikiPage(object):

    def nextURL(self):
        return '../'+self.context.contentName


class EditWikiPage(object):

    def update(self):
        status = super(EditWikiPage, self).update()

        if Update in self.request:
            self.request.response.redirect('./@@view.html')

        return status


class ViewWikiPage(object):
    """A rendered View of the wiki page."""

    def renderWikiLinks(self, html):
        """Add Wiki Links to the source"""
        html = protectedLine.sub(self._protectLine, html)
        html = interwikilink.sub(self._interwikilinkReplace, html)
        html = wikilink.sub(self._wikilinkReplace, html)
        return html

    def render(self):
        """Render the wiki page source."""
        source = zapi.createObject(self.context.type, self.context.source)
        view = zapi.getMultiAdapter((removeAllProxies(source), self.request))
        html = view.render()
        html = self.renderWikiLinks(html)
        return html

    def comments(self):
        result = []
        for name, comment in self.context.items():
            dc = DublinCoreViews(comment, self.request)
            source = zapi.createObject(comment.type, comment.source)
            view = zapi.getMultiAdapter(
                (removeAllProxies(source), self.request))
            result.append({
                'name': name,
                'title': comment.title,
                'author': dc.author(),
                'modified': dc.modified(),
                'text': view.render()
                })

        return result

    def _protectLine(self, match):
        return wikilink.sub(r'!\1', match.group(1))

    def _wikilinkReplace(self, match, allowed=0, state=None, text=''):
        # tasty spaghetti regexps! better suggestions welcome ?
        """
        Replace an occurrence of the wikilink regexp or one of the
        special [] constructs with a suitable hyperlink

        To be used as a re.sub repl function *and* get a proper value
        for literal context, 'allowed', etc, enclose this function
        with the value using 'thunk_substituter'.
        """
        # In a literal?
        if state is not None:
            if within_literal(match.start(1), match.end(1)-1, state, text):
                return match.group(1)

        # matches beginning with ! should be left alone
        if re.match('^!', match.group(0)):
            return match.group(1)

        m = morig = match.group(1)
        wiki = getParent(self.context)

        # if it's a bracketed expression,
        if bracketedexpr.match(m):

            # strip the enclosing []'s
            m = bracketedexpr.sub(r'\1', m)

            # extract a (non-url) path if there is one
            pathmatch = re.match(r'(([^/]*/)+)([^/]+)', m)
            if pathmatch:
                path, id = pathmatch.group(1), pathmatch.group(3)
            else:
                path, id = '', m

            # or if there was a path assume it's to some non-wiki
            # object and skip the usual existence checking for
            # simplicity. Could also attempt to navigate the path in
            # zodb to learn more about the destination
            if path:
                return '<a href="%s%s">%s%s</a>' % (path, id, path, id)

            # otherwise fall through to normal link processing

        # if it's an ordinary url, link to it
        if url.match(m):
            return m

        # it might be a structured text footnote ?
        elif re.search(r'(?si)<a name="%s"' % (m),text):
            return '<a href="#%s">[%s]</a>' % (m,m)

        # a wikiname - if a page (or something) of this name exists, link to
        # it
        elif m in wiki:
            return '<a href="../%s">%s</a>' % (quote(m), m)

        # otherwise, provide a "?" creation link
        else:
            return '%s<a href="../+/AddWikiPage.html=%s">?</a>' %(
                morig, quote(m))


    def _interwikilinkReplace(self, match, allowed=0, state=None, text=''):
        """Replace an occurrence of interwikilink with a suitable hyperlink.

        To be used as a re.sub repl function *and* get a proper value
        for literal context, 'allowed', etc.
        """
        # matches beginning with ! should be left alone This is a bit naughty,
        # but: since we know this text will likely be scanned with
        # _wikilink_replace right after this pass, leave the ! in place for it
        # to find. Otherwise the localname will get wiki-linked.
        if re.match('^!', match.group(0)):
            return match.group(0)

        localname  = match.group('local')
        remotename = match.group('remote') # named groups come in handy here!

        # NB localname could be [bracketed]
        if bracketedexpr.match(localname):
            localname = bracketedexpr.sub(r'\1', localname)

        # look for a RemoteWikiURL definition
        if hasattr(getParent(self.context), localname):
            localpage = getattr(self.aq_parent,localname)
            # local page found - search for "RemoteWikiUrl: url"
            m = re.search(remotewikiurl, str(localpage))
            if m is not None:
                remoteurl = html_unquote(m.group(1))

                # we have a valid inter-wiki link
                link = '<a href="%s%s">%s:%s</a>' % \
                       (remoteurl, remotename, localname, remotename)
                # protect it from any later wiki-izing passes
                return wikilink.sub(r'!\1', link)

        # otherwise, leave alone
        return match.group(0)


class EditWikiParents(object):

    def parents(self):
        hier = IWikiPageHierarchy(self.context)
        return hier.parents

    def availableWikis(self):
        wiki = getParent(self.context)
        return wiki.keys()

    def setParents(self, parents):
        hier = IWikiPageHierarchy(self.context)
        hier.reparent(parents)
        return self.request.response.redirect('./@@parents.html')

    def _branchHTML(self, children):
        html = '<ul>\n'
        for child, subs in children:
            html += ' <li><a href="../%s">%s</a></li>\n' %(getName(child),
                                                           getName(child))
            if subs:
                html += self._branchHTML(subs)
        html += '</ul>\n'
        return html

    def branch(self):
        hier = IWikiPageHierarchy(self.context)
        children = hier.findChildren()
        return self._branchHTML(children)


class AddComment(object):

    def nextURL(self):
        return '../'


class MailSubscriptions(object):

    def subscriptions(self):
        return IMailSubscriptions(self.context).getSubscriptions()

    def change(self):
        if 'ADD' in self.request:
            emails = self.request['emails'].split('\n')
            IMailSubscriptions(self.context).addSubscriptions(emails)
        elif 'REMOVE' in self.request:
            emails = self.request['remails']
            print emails
            if isinstance(emails, (str, unicode)):
                emails = [emails]
                IMailSubscriptions(self.context).removeSubscriptions(emails)

        self.request.response.redirect('.')
