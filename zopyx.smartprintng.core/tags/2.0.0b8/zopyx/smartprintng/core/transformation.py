##########################################################################
# zopyx.smartprintng.core - high-quality export of Plone content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

""" HTML transformation classes (based on BeautifulSoup) """

import re
from BeautifulSoup import BeautifulSoup, NavigableString, Tag

import zope.component
from zope.component.factory import Factory
from zope.component.interfaces import IFactory
from zope.interface import implements

from interfaces import IHTMLTransformation


def registerTransformation(cls):
    """ Register factories for transformation classes """

    gsm = zope.component.getGlobalSiteManager()
    f = Factory(cls, cls.name)
    gsm.registerUtility(f, IFactory, cls.name)
    gsm.registerUtility(cls, IHTMLTransformation, cls.name)

class BaseTransform(object):

    def __init__(self, html=None, soup=None):
        if not html and not soup:
            raise ValueError("'html' and 'soup' can not be both None")
        self.soup = (soup is not None) and soup or BeautifulSoup(html)

    def __str__(self):
        return self.soup.renderContents()

    def transform(self):
        raise NotImplementedError("Do not instantiate BaseTransform directly")


class LinkRemover(BaseTransform):
    implements(IHTMLTransformation)

    name = 'zopyx.smartprintng.linkremover'
    description = 'Removes links from HTML'

    def transform(self):
        """ replace all links with a <span> tag and the anchor text """

        soup = self.soup
        refs = soup.findAll('a')

        for x in refs:
            tag = Tag(soup, 'span')
            tag.insert(0, x.renderContents().strip())
            soup.a.replaceWith(tag)


class ReviewHistoryRemover(BaseTransform):
    implements(IHTMLTransformation)

    name = 'zopyx.smartprintng.reviewhistoryremover'
    description = 'Removes the review history from HTML'

    def transform(self):
        """ replace all links with a <span> tag and the anchor text """

        soup = self.soup
        for x in soup.findAll(id='review-history'):
            x.extract()


class ImageRemover(BaseTransform):
    implements(IHTMLTransformation)

    name = 'zopyx.smartprintng.imageremover'
    description = 'Removes images from HTML'

    def transform(self):
        """ Remove all images """

        soup = self.soup
        images = soup.findAll('img')
        [img.extract() for img in images]


class LinkListAdder(BaseTransform):
    implements(IHTMLTransformation)

    name = 'zopyx.smartprintng.linklistadder'
    description = 'Add a numbered link list to the end of the document'

    def _pcdataFromNode(self, s, lst=[]):
        """ recursive pcdata collector """

        if s.string is not None:
            lst.append(s.string)
        else:
            for n in s.contents:
                self._pcdataFromNode(n, lst)
        return ' '.join(lst)

    def checkHref(self, href):
        """ Return False for mailto|javascript or internal
            anchors or views.
        """

        if 'mailto:' in href or \
           'javascript:' in href or \
           href.startswith('#') or \
           href.startswith('@@'):
               return False
        return True
           

    def getLinksInHtml(self):
        """ return all links inside a HTML fragment """

        soup = self.soup
        hrefs = []
        for anchor in soup.findAll('a'):

            # we need to capture internal anchors
            try:
                href = anchor['href']
            except:
                continue 

            if href in hrefs or not self.checkHref(href):
               continue
            hrefs.append(str(href))
        return hrefs


    def enumerateLinks(self):

        count = 1
        links = []
        soup = self.soup
        for anchor in soup.findAll('a'):

            # capture internal anchors
            try:
                href = anchor['href']
            except KeyError:
                continue

            if not self.checkHref(href):
                continue

            anchor['class'] = 'enumerated-link'
            s = self._pcdataFromNode(anchor) + ' [%d]' % count
            anchor.contents = [NavigableString(s)]
            links.append(anchor['href'])
            count += 1
        return links            


    def transform(self):

        links = self.getLinksInHtml()
        self.enumerateLinks()
        soup = self.soup

        if links:
            pat = '<li>[%d] %s</li>'
            div = Tag(soup, 'div')
            div['id'] = 'enumerated-links'
            ol = Tag(soup, 'ol')
            div.append(ol)
            soup.append(div)

            for i, link in enumerate(links):
                li = Tag(soup, 'li')
                li.append(NavigableString(u'[%d] %s' % (i+1, link)))
                ol.append(li)


class PageBreaker(BaseTransform):
    implements(IHTMLTransformation)

    name = 'zopyx.smartprintng.pagebreaker'
    description = 'Adds page breaks at H1/H2 elements'

    def transform(self, separator='(h1|h2)'):

        html = str(self)
        breaker = re.compile('<%s' % separator, re.I|re.M|re.S)

        div_start = '<div class="chapter sp-page">'
        div_start2 = '<div class="chapter">'
        div_end = '</div>'

        positions = []
        for mo in breaker.finditer(html):
            positions.append(mo.start())
        positions.append(len(html))

        parts = []
        len_positions = len(positions) - 1
        for i in range(len_positions):
            start = positions[i]
            end = positions[i+1]

            if i == len_positions - 1:
                parts.append(div_start2 + html[start: end].strip() + div_end)
            else:
                parts.append(div_start + html[start: end].strip() + div_end)

        html2 = '\n'.join(parts)
        self.soup = BeautifulSoup(html2)


class EmptyElementRemover(BaseTransform):
    implements(IHTMLTransformation)

    name = 'zopyx.smartprintng.emptyelementremover'
    description = 'Removes empty elements from document'

    def transform(self, remove_elements=('p', 'div')):
        soup = self.soup
        for e in soup.findAll(remove_elements):
            if not e.contents:
                e.extract()


class LinksToPrinceFootnotes(BaseTransform):
    implements(IHTMLTransformation)

    name = 'zopyx.smartprintng.linkstoprincefootnotes'
    description = 'Convert links to external URLs to PrinceXML footnotes'

    def transform(self):
        soup = self.soup
        for a in soup.findAll('a'):

            try:
                href = a['href']
            except KeyError:
                continue

            if not re.match(r'^(http|http|ftp)://', href):
                continue

            contents = a.contents
            span1 = Tag(soup, 'span')
            span1['class'] = 'generated-footnote-text'
            span1.insert(0, NavigableString(contents[0]))
            span2 = Tag(soup, 'span')
            span2['class'] = 'generated-footnote'
            span2.insert(0, NavigableString(href))
            span1.insert(1, span2)
            a.replaceWith(span1)




# register factories for all transformations
import inspect
for x in locals().values():
    if inspect.isclass(x) and IHTMLTransformation.implementedBy(x):
        registerTransformation(x)
