import jsontemplate
from zope.interface import implements
from hurry.custom.interfaces import ITemplate, CompileError, RenderError

class JsonTemplate(object):
    implements(ITemplate)

    def __init__(self, source):
        try:
            self.json_template = jsontemplate.Template(source)
        except jsontemplate.CompilationError, e:
            raise CompileError(unicode(e))
        self.source = source
        
    def __call__(self, input):
        try:
            return self.json_template.expand(input)
        except jsontemplate.EvaluationError, e:
            raise RenderError(unicode(e))

        
