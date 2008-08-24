import re
import urlparse

import grok
from zope.interface import Interface

class ITransform(Interface):
    pass

class WikiWords(grok.Adapter):
    """Translates WikiWords to links.
    We look up all words, and we only link those words that currently exist.
    """
    grok.implements(ITransform)
    grok.name('wiki.WikiWords')
    grok.context(grok.View)
  
    def run(self):
        regexp = re.compile(r'[A-Z][a-z]+([A-Z][a-z]+)+')
        return regexp.sub(self.replace, self.context.content)

    def replace(self, match):
        wikiword = match.group(0)
        if wikiword in self.context.wordlist:
            return '<a class="wikiword" href="%s/%s">%s</a>' % \
        (urlparse.urlparse(self.context.application_url())[2],wikiword, wikiword)
        else:
            return wikiword


class AutoLink(grok.Adapter):
    """A transform that auto-links URLs."""
    grok.implements(ITransform)
    grok.name('wiki.AutoLink')
    grok.context(grok.View)
  
    def run(self):
        regexp = re.compile(r'([^"])\b((http|https)://[^ \t\n\r<>\(\)&"]+' \
                            r'[^ \t\n\r<>\(\)&"\.])')
        return regexp.sub(self.replace, self.context.content)
    
    def replace(self, match):
        url = match.group(2)
        return '<a class="autourl" href="%s">%s</a>' % (url, url)


class ListOfPages(grok.Adapter):
    """A transform that adds a TOC list to the default page"""
    grok.implements(ITransform)
    grok.name('wiki.ListOfPages')
    grok.context(grok.View)
    
    def run(self):
        if self.context.page_name == self.context.default_page_name:
            if self.context.wordlist:
                return self.context.content + '<div id="toc"><b>Available Pages:\
                </b> %s</div>' % ', '.join(self.context.wordlist)
        return self.context.content

