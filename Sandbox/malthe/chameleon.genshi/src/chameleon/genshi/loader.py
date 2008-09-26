from chameleon.core.loader import TemplateLoader as BaseLoader
from chameleon.core.genshi import language
from chameleon.core.genshi import template


class TemplateLoader(BaseLoader):
    default_parser = language.Parser()

    def load(self, filename):
        return super(BaseLoader, self).load(filename,
                klass=template.GenshiTemplateFile)

