"""
A grok.AtomFeed syndicates sub-objects into an Atom feed.

  >>> box = MammothBox()
  >>> getRootFolder()["box"] = box

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/box/@@atom")
  >>> print browser.contents
  <?xml version="1.0" encoding="utf-8" ?>
  <?xml-stylesheet href="atom.css" type="text/css"?>
  <feed xmlns="http://www.w3.org/2005/Atom"
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xml:base="" xml:lang="en">
    <title type="html">This is the title</title>
    <subtitle>A box full of mammoths.</subtitle>
  <BLANKLINE>
    <updated>2008-07...</updated>
  <BLANKLINE>
    <link rel="alternate" type="text/html"/>
  <BLANKLINE>
    <link rel="self" type="application/atom+xml"
          href="CANNA KNOW THIS, CAPTN!"/>
  <!-- XXX TODO: Use this, it's better!
          tal:attributes="href string:${view/absolute_url}" -->
  <BLANKLINE>
  <BLANKLINE>
  <BLANKLINE>
    <id>urn:syndication:xyzzy</id>
  <BLANKLINE>
  <BLANKLINE>
  <BLANKLINE>
  <BLANKLINE>
  </feed>
  <BLANKLINE>
  
"""
import grok
from zope import schema
from zope.schema.fieldproperty import FieldProperty

#

from zope.interface import Interface

class IMammoth(Interface):
    name = schema.TextLine(title=u"Name")
    size = schema.TextLine(title=u"Size", default=u"Quite normal")

class MammothBox(object):
    pass

class Mammoth(grok.Model):
    grok.implements(IMammoth)
    name = FieldProperty(IMammoth['name'])    
    size = FieldProperty(IMammoth['size'])    

# The actions necessary to put a Feed on top of these objects.

from megrok.feeds.components import Feed, AtomFeed
#from vice.outbound.core.interfaces import IFeedItem
from datetime import datetime

class Atom(AtomFeed):
    """This is what makes /atom return an Atom feed."""

class MammothBoxFeed(Feed):
    """This makes a MammothBox able to be rendered as a feed."""
    grok.context(MammothBox)

    def __init__(self, context):
        self.context = context
        self.description = 'A box full of mammoths.'
        self.modified = datetime.now()
        self.name = 'This Mammoth Box'
        self.title = 'This is the title'
        self.UID = 'xyzzy'
        self.alternate_url = 'ALT'

    @property
    def context_url(self):
        return grok.url(context)

    @property
    def self_url(self):
        return 'CANNA KNOW THIS, CAPTN!'

    def __iter__(self):
        while False:
            yield None

#class MammothItem(grok.Adapter):
#    """This makes a Mammoth eligible to appear as a feed item."""
#    grok.context(Mammoth)
#    grok.implements(IFeedItem)
#    def __init__(self, context):
#        self.context = context
#        self.title = 'Mammoth %s' % self.name

