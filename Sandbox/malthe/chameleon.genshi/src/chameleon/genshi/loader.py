from chameleon.core.loader import TemplateLoader as BaseLoader
from chameleon.genshi import language
from chameleon.genshi import template


class TemplateLoader(BaseLoader):
    default_parser = language.Parser()

    def load(self, filename):
        return super(TemplateLoader, self).load(filename,
                template.GenshiTemplateFile)

