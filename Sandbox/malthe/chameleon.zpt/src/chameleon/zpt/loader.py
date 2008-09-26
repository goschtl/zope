from chameleon.core.loader import TemplateLoader as BaseLoader
from chameleon.core.zpt import language
from chameleon.core.zpt import template

class TemplateLoader(BaseLoader):
    default_parser = language.Parser()

    def load(self, filename):
        return super(BaseLoader, self).load(filename,
                klass=template.PageTemplateFile)


