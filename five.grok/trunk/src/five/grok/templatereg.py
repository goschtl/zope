import grokcore.component

from grokcore.view.components import PageTemplate
from grokcore.view.interfaces import ITemplateFileFactory

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class ZopeTwoPageTemplate(PageTemplate):

    def setFromString(self, string):
        raise NotImplemented

    def setFromFilename(self, filename, _prefix=None):
        self._template = ViewPageTemplateFile(filename, _prefix)
    
    def render(self, view):
        namespace = self.getNamespace(view)
        template = self._template.__of__(view)
        namespace.update(template.pt_getContext())
        return template(namespace)

class ZopeTwoPageTemplateFileFactory(grokcore.component.GlobalUtility):
    grokcore.component.implements(ITemplateFileFactory)
    grokcore.component.name('pt')

    def __call__(self, filename, _prefix=None):
        return ZopeTwoPageTemplate(filename=filename, _prefix=_prefix)