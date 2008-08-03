import grokcore.component
from grokcore.view.interfaces import ITemplateFileFactory

from five.grok.components import ZopeTwoPageTemplate

class ZopeTwoPageTemplateFileFactory(grokcore.component.GlobalUtility):
    grokcore.component.implements(ITemplateFileFactory)
    grokcore.component.name('pt')

    def __call__(self, filename, _prefix=None):
        return ZopeTwoPageTemplate(filename=filename, _prefix=_prefix)