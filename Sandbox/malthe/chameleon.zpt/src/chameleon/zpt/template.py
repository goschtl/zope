from zope import i18n

from chameleon.core import template
from chameleon.core import config

import language

def prepare_language_support(**kwargs):
    target_language = kwargs.get('target_language')

    if config.DISABLE_I18N:
        if target_language:
            del kwargs['target_language']
        return
    
    if not target_language:
        context = kwargs.get(config.SYMBOLS.i18n_context)
        target_language = i18n.negotiate(context)

        if target_language:
            kwargs['target_language'] = target_language    

class PageTemplate(template.Template):
    __doc__ = template.Template.__doc__ # for Sphinx autodoc

    default_parser = language.Parser()
    
    def __init__(self, body, parser=None, format=None, doctype=None):
        if parser is None:
            parser = self.default_parser
        super(PageTemplate, self).__init__(body, parser, format, doctype)

    def render(self, **kwargs):
        prepare_language_support(**kwargs)
        return super(PageTemplate, self).render(**kwargs)

class PageTemplateFile(template.TemplateFile):
    __doc__ = template.TemplateFile.__doc__ # for Sphinx autodoc

    default_parser = language.Parser()
    
    def __init__(self, filename, parser=None, format=None,
                 doctype=None, **kwargs):
        if parser is None:
            parser = self.default_parser
        super(PageTemplateFile, self).__init__(filename, parser, format,
                                               doctype, **kwargs)

    def render(self, **kwargs):
        prepare_language_support(**kwargs)
        return super(PageTemplateFile, self).render(**kwargs)
