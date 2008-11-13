from chameleon.core import template

import os
import language

class DynamicHTMLFile(template.TemplateFile):
    def __init__(self, filename, **kwargs):
        parser = self.parser = language.DynamicHTMLParser(filename)
        super(DynamicHTMLFile, self).__init__(
            filename, parser, **kwargs)

    def render(self, content={}, attributes={}, **kwargs):
        return template.TemplateFile.render(
            self, content=content, attributes=attributes, **kwargs)

    def render_macro(self, macro, global_scope=False, parameters=None):
        if parameters is None: parameters = {}
        
        parameters.setdefault('content', {})
        parameters.setdefault('attributes', {})

        return template.TemplateFile.render_macro(
            self, macro, global_scope=global_scope, parameters=parameters)

    def mtime(self):
        """Return the most recent modification times from the template
        file itself and any XSS-files included."""

        filenames = [self.filename]
        filenames.extend(self.parser.file_dependencies)
        
        try:
            return max(map(os.path.getmtime, filenames))
        except (IOError, OSError):
            return 0
        
