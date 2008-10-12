
from grokcore.view.components import PageTemplate
from grokcore.view.interfaces import ITemplateFileFactory

from five import grok
from five.pt.pagetemplate import ViewPageTemplateFile, ViewPageTemplate

class ZopeTwoPageTemplate(PageTemplate):

    def setFromString(self, string):
        self._template = ViewPageTemplate

    def setFromFilename(self, filename, _prefix=None):
        self._template = ViewPageTemplateFile(filename, _prefix)

    def _initFactory(self, factory):
        pass

    def render(self, view):
        namespace = self.getNamespace(view)
        return self._template.render(view, default_namespace=namespace)()


class ZopeTwoPageTemplateFileFactory(grok.GlobalUtility):
    grok.implements(ITemplateFileFactory)
    grok.name('zpt')

    def __call__(self, filename, _prefix=None):
        return ZopeTwoPageTemplate(filename=filename, _prefix=_prefix)
