"""A preview that declares something is not previewable.
"""

from zope import component, interface
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.formlib import namedtemplate
import zope.publisher.browser
from zope.publisher.interfaces.browser import IBrowserRequest

class Preview(zope.publisher.browser.BrowserPage):
    interface.implements(interface.Interface)
    
    template = namedtemplate.NamedTemplate('default')

    def __call__(self):
        return self.template()

default_template = namedtemplate.NamedTemplateImplementation(
    ViewPageTemplateFile('default.pt'),
    Preview
    )
