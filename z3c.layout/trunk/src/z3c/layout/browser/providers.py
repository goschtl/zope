from zope import interface
from lxml import html

import interfaces

class HtmlHead(object):
    """Tree content provider mixin.

    Appends rendered content into the HTML <head>.
    """

    interface.implements(interfaces.ITreeContentProvider)
        
    def insert(self, tree):
        head = tree.find('.//head')
        if head is not None:
            provided = html.fromstring(
                u"<div>%s</div>" % self.render())

            if len(head) > 0:
                head[-1].tail = provided.text
            else:
                head.text = provided.text

            head.extend(tuple(provided))

class HtmlTop(object):
    """Tree content provider mixin.

    Prepends rendered content to HTML <body>.
    """

    interface.implements(interfaces.ITreeContentProvider)
    
    def insert(self, tree):
        body = tree.find('.//body')
        if body is not None:
            provided = html.fromstring(
                u"<div>%s</div>" % self.render())

            provided.tail = body.text
            body.text = provided.text

            for element in reversed(provided):
                body.insert(0, element)

class HtmlBottom(object):
    """Tree content provider mixin.

    Appends rendered content to HTML <body>.
    """

    interface.implements(interfaces.ITreeContentProvider)
    
    def insert(self, tree):
        body = tree.find('.//body')
        if body is not None:
            provided = html.fromstring(
                u"<div>%s</div>" % self.render())

            if len(body) > 0:
                body[-1].tail = provided.text
            else:
                body.text = provided.text
            
            body.extend(tuple(provided))
