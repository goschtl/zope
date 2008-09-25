from chameleon.core import template

import language

class DynamicHTMLFile(template.TemplateFile):
    def __init__(self, filename, **kwargs):
        parser = language.DynamicHTMLParser(filename)
        super(DynamicHTMLFile, self).__init__(
            filename, parser, **kwargs)
