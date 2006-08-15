"""Very simple preview-view. It displays content in an iframe with its
source link pointing to the 'inline' view on the content.
"""

from zope import component, interface
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.formlib import namedtemplate
import zope.publisher.browser
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.mimetype.types import IContentTypeMicrosoftWord

class Preview(zope.publisher.browser.BrowserPage):
    interface.implements(interface.Interface)
    
    template = namedtemplate.NamedTemplate('iframe')

    def __call__(self):
        return self.template()

default_template = namedtemplate.NamedTemplateImplementation(
    ViewPageTemplateFile('iframe.pt'),
    Preview
    )
