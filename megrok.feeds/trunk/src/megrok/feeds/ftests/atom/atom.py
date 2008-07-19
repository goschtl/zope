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
from zope.interface import Interface, implements
from zope.schema.fieldproperty import FieldProperty

#

#from megrok.feeds
from vice.outbound.core.browser.feed import Atom_1_0_FeedView
from vice.outbound.core.interfaces import IFeed, IFeedItem

from zope.interface import Interface
class IFeedable(Interface):
    pass # marker interface

# need three things:
# (1) we need to create an adapter from MammothBox to IFeed
# (2) we need to mark MammothBox as IFeedable
# (3) we need to create a View that makes an IFeedable render

#

class IMammoth(Interface):
    name = schema.TextLine(title=u"Name")
    size = schema.TextLine(title=u"Size", default=u"Quite normal")

class MammothBox(object): #grok.Container): #grok.Application, #grok.Container
    implements(IFeedable) #(2)

from datetime import datetime

class MammothBoxFeed(grok.Adapter): #(1)
    grok.context(MammothBox)
    grok.provides(IFeed)
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

#class AtomFormat(Atom_1_0_FeedView): #, grok.View):
#    grok.context(IFeedable)
    #@grok.require('zope.View')
    #def __call__(self, *args, **kw):
    #    super(self, AtomFormat).__call__(self, *args, **kw)

from megrok.feeds.components import AtomFeed

class Atom(AtomFeed):
    grok.context(IFeedable)

#class AtomFormat(Atom_1_0_FeedView): #, grok.View):
#    grok.context(IFeedable)


from zope.component import provideAdapter
from zope.publisher.interfaces.browser import IBrowserPage, IBrowserView
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

class Mammoth(grok.Model):
    implements(IMammoth)
    
    name = FieldProperty(IMammoth['name'])    
    size = FieldProperty(IMammoth['size'])    

class MammothItem(grok.Adapter): #(3)
    grok.context(Mammoth)
    grok.implements(IFeedItem)
    def __init__(self, context):
        self.context = context
        self.title = 'Mammoth %s' % self.name
        # DUH, don't need this yet, will finish later
