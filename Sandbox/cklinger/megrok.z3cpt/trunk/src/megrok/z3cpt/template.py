import grok
import os
from z3c.pt.pagetemplate import PageTemplate, PageTemplateFile

class z3cPageTemplate(grok.components.GrokTemplate):

    def setFromString(self, string):
        self._template = PageTemplate(string)

    def setFromFilename(self, filename, _prefix=None):
	filename = os.path.join(_prefix, filename)
        self._template = PageTemplateFile(filename)

    def render(self, view):
        return self._template.render(**self.getNamespace(view))


class Z3CPTemplateFactory(grok.GlobalUtility):

    grok.implements(grok.interfaces.ITemplateFileFactory)
    grok.name('3pt')

    def __call__(self, filename, _prefix=None):
        return z3cPageTemplate(filename=filename, _prefix=_prefix)

