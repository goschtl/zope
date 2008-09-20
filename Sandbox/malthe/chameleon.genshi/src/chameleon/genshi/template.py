from chameleon.core import template
from chameleon.core import config

import language

class GenshiTemplate(template.Template):
    __doc__ = template.Template.__doc__ # for Sphinx autodoc

    default_parser = language.Parser()
    
    def __init__(self, body, parser=None, format=None, doctype=None):
        if parser is None:
            parser = self.default_parser
        super(GenshiTemplate, self).__init__(body, parser, format, doctype)

class GenshiTemplateFile(template.TemplateFile):
    __doc__ = template.TemplateFile.__doc__ # for Sphinx autodoc

    default_parser = language.Parser()
    
    def __init__(self, filename, parser=None, format=None,
                 doctype=None, **kwargs):
        if parser is None:
            parser = self.default_parser
        super(GenshiTemplateFile, self).__init__(
            filename, parser, format, doctype, **kwargs)
