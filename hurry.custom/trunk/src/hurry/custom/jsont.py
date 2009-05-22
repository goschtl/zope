import jsontemplate
from zope.interface import implements
from hurry.custom.interfaces import ITemplate

class JsonTemplate(object):
    implements(ITemplate)

    def __init__(self, source):
        self.json_template = jsontemplate.Template(source)
        self.source = source
        
    def __call__(self, input):
        return self.json_template.expand(input)

        
