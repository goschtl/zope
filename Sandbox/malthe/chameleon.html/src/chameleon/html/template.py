from chameleon.core import template

import language

class DynamicHTMLFile(template.TemplateFile):
    def __init__(self, filename, **kwargs):
        parser = self.parser = language.DynamicHTMLParser(filename)
        super(DynamicHTMLFile, self).__init__(
            filename, parser, **kwargs)

    def render(self, content={}, attributes={}, **kwargs):
        return template.TemplateFile.render(
            self, content=content, attributes=attributes, **kwargs)
