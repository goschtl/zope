from chameleon.core.loader import TemplateLoader as BaseLoader
from chameleon.core.genshi import language

class TemplateLoader(BaseLoader):
    def __init__(self, *args, **kwargs):
        if "parser" not in kwargs:
            kwargs["parser"] = language.Parser()

        super(BaseLoader, self).__init__(*args, **kwargs)

