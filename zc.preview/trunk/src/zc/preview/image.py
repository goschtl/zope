"""Very simple preview-view for images.
"""

from zope import interface
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.formlib import namedtemplate
import zope.publisher.browser

class Preview(zope.publisher.browser.BrowserPage):
    interface.implements(interface.Interface)

    template = namedtemplate.NamedTemplate('image')

    def __call__(self):
        return self.template()

default_template = namedtemplate.NamedTemplateImplementation(
    ViewPageTemplateFile('image.pt'),
    Preview
    )
