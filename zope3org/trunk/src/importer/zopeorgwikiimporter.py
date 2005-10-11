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
"""Importers

$Id: $
"""
import re
import urllib
import HTMLParser
from datetime import datetime

import zope.component
import zope.interface

from zope.app.file import File
from zope.app.container.interfaces import IContainer
from zope.app.dublincore.interfaces import IZopeDublinCore

from importer import IImporter

index_name = 'index'

protocol = re.compile('.*?://')
notFound = re.compile('Bobo-Exception-Type:\s*NotFound')

class ImporterForContainer(object):
    """Imports a whole (sub)site into a container
    """
    zope.interface.implements(IImporter)
    zope.component.adapts(IContainer)
    
    def __init__(self, context):
        self.context = context

    def download(self, url, base_url=None):
        """See IImporter
        """
        base_fetch_url, relative_url = url.rsplit('/', 1)
        if base_url is None:
            base_url = base_fetch_url
        
        self.base_fetch_url = base_fetch_url
        self.base_url = base_url
        
        self._recursiveImport(relative_url)
    
    def _recursiveImport(self, relative_url):
        """Recurses into all local links of subdocuments
        
        The ``url`` has to be relative to the base.
        """
        url = "%s/%s" % (self.base_fetch_url, relative_url)
        
        # retrieve the page
        doc = urllib.urlopen(url)
        headers = ''.join(doc.info().headers)
        
        # check for zope2 NotFound exceptions
        # XXX this is zope specific, arghh!
        if notFound.search(headers) is not None:
            raise IOError('404 NotFound')
            
        # XXX make a utiliy lookup of this
        parser = ZopeOrgWikiPageExtractor()
        parser.feed(doc.read())
        text = parser.getText()
        links = parser.getLinks()
        
        # parse the metadata in rdf format
        if self.base_fetch_url.startswith('file:'):
            sep = '.'
        else:
            sep = '/'
        metadata_url = "%s%srdf_view.rdf" % (url, sep)
        metadata_rdf = urllib.urlopen(metadata_url)
        metadata = {}
        for line in metadata_rdf.readlines():
            mdata = extractDublinCore(line)
            if mdata is None:
                continue
            metadata[mdata[0]] = unicode(mdata[1])
        
        file = File(text, metadata['format'])

        # we don't notify with a ``ObjectCreatedEvent`` because
        # we don't want the created and modification date to be set

        dc = IZopeDublinCore(file)
        dc.title = metadata['title']
        dc.format = metadata['format']
        dc.creators = (metadata['creator'],)
        y, m, d = metadata['created'].split('-')
        dc.created = datetime(int(y), int(m), int(d))
        y, m, d = metadata['modified'].split('-')
        dc.modified = datetime(int(y), int(m), int(d))
        
        # XXX what data to be set else? (type="Wiki Page")
        # XXX there is also a ``date``, hmmm?
        
        self.context[metadata['title']] = file
        
        # XXX notify ObjectAddedEvent
        pass

        # filter out all not internal links and duplicates
        internal_links = {}
        base_url_len = len(self.base_url) + 1
        for link in links:
            # collect absolute internal link
            if link.startswith(self.base_url):
                relative_link = link[base_url_len:]
                # check for not yet written page
                if relative_link.find('?') != -1:
                    newPageString = '%s/editform\?page=(.*)' % relative_url
                    np = re.compile(newPageString).match(relative_link)
                    if np is None:
                        pass # log an anomaly
                    else:
                        relative_link = np.groups()[0]
                internal_links[relative_link] = True
                continue

            # ignore links to anchors and external links
            if link.startswith('#') or protocol.match(link):
                continue

            # collect relative internal link
            internal_links[link] = True
        
        internal_links = internal_links.keys()

        # recurse into links (attentions some are relative)
        for link in internal_links:
            try:
                self._recursiveImport(link)
            except IOError:
                pass

# matches the following type of data:
#    <dc:date>2003-08-04</dc:date>
#    <dcterms:created>2003-08-01</dcterms:created>
rdfdc = re.compile('<(?:dc|dcterms):(.*?)>(.*?)</(?:dc|dcterms):.*?>')
#    <dc:creator rdf:resource="http://www.zope.org/Members/Brian"/>
rdfrsc =re.compile('<dc:(.*?)\s+rdf:resource="(.*?)"\s*/\s*>')

def extractDublinCore(line):
    """Extracting dublin core data with regular expressions
    """
    dc = rdfdc.search(line)
    if dc is not None:
        return dc.groups()
    rsc = rdfrsc.search(line)
    if rsc is not None:
        return rsc.groups()


class ZopeOrgWikiPageExtractor(HTMLParser.HTMLParser):
    """Extracts www.zope.org wiki pages (plone 1.0 based site)
    """

    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self._text = ['<html><head></head><body>']
        self._links = []
        self.inMain = False
        self.inContent = False
        self.done = False

    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        
        tag = Tag(tag, attrs)
        
        # search for content
        if tag.matches('td', 'class', 'main'):
            self.inMain = True
        elif self.inMain and tag.matches('h1'):
            self.inContent = True
        elif self.inContent and tag.matches('div'):
            self.possibleEndOfContent = len(self._text)
        elif self.inContent and tag.matches('a'):
            if tag.matches('a', 'name', 'bottom'):
                # remove content up to and including previous ``<div>``
                self._text = self._text[:self.possibleEndOfContent]
                self.done = True
                self.inContent = False
            elif tag.matches('a', 'href'):
                self._links.append(tag.getAttribute('href'))
        
        # add content to the result
        if self.inContent:
            self._text.append(tag())

    def handle_endtag(self, tag):
        if self.inContent:
            self._text.append("</%s>" % tag)
    
    def handle_data(self, data):
        if self.inContent:
            self._text.append(data)

    def handle_charref(self, name):
        if self.inContent:
            self._text.append("&#%s;" % name)

    def handle_entityref(self, name):
        if self.inContent:
            self._text.append("&%s;" % name)

    def getText(self):
        self._text.append('</body></html>')
        return ''.join(self._text)
    
    def getLinks(self):
        return self._links


class Tag(object):
    """Tag management
    """
    
    def __init__(self, tag, attrs):
        self._tag = tag
        self._attrs = attrs
        
        # dictify the attrs passed to ``handle_starttag`` method
        attr_dict = {}
        for key, val in attrs:
            attr_dict[key] = val
        self._attr_dict = attr_dict
        
    def matches(self, tag_name=None, attr_key=None, attr_value=None):
        """Returns ``True`` if a tag matches
        
            >>> tag = Tag("td", (("class", "highlighted"), ("blah", "5")))
        
        Check for a specific tag only (ignoring attributes)::
        
            >>> tag.matches(tag_name="td")
            True
            >>> tag.matches(tag_name="h1")
            False
        
        Check for the existence of an attribute (the tag is irrelevant)::
        
            >>> tag.matches(attr_key="class")
            True
        
        Check for a specific tag with a specific attribute where the value 
        of the attribute is irrelevant::
        
            >>> tag.matches(tag_name="td", attr_key="class")
            True
        
        Check for a specific tag, attribute combination::
        
            >>> tag.matches(tag_name="td", attr_key="class", 
            ...             attr_value="highlighted")
            True
            
        Check for not existing attribute::
        
            >>> tag.matches(tag_name="td", attr_key="gaga")
            False
        """
        if tag_name in (None, self._tag):
            if attr_key is None:
                return True
            if attr_value is None and attr_key in self._attr_dict:
                return True
            if self._attr_dict.get(attr_key, object()) == attr_value:
                return True
                
        return False
        
    def __call__(self):
        """Returns the whole tag
        """
        tag = ["<%s" % self._tag]
        for keyval in self._attrs:
            tag.append(" %s=%s" % keyval)
        tag.append(">")
        return ''.join(tag)
    
    def getAttribute(self, key):
        """Returns the value of a specific attribute
        """
        return self._attr_dict[key]
