from Zope.Publisher.Browser.BrowserView import BrowserView
from Interface import Interface
from Schema.IField import IField
from Zope.ComponentArchitecture import getView
import Schema
from Schema import _Schema # XXX wire up, should really fix this :)

class ITestSchema(Interface):
    alpha = Schema.Str(title="Alpha")
    beta = Schema.Bool(title="Beta")
    
class FormView(BrowserView):
    def getWidgetsForSchema(self, schema, view_name):
        """Given a schema and a desired field name, get a list of
        widgets for it.
        """
        result = []
        for name in schema.names(1):
            attr = schema.getDescriptionFor(name)
            if IField.isImplementedBy(attr):
                widget = getView(attr, view_name, self.request)
                result.append(widget)
        return result

    def getFields(self):
        """XXX just a test method.
        """
        result = self.getWidgetsForSchema(ITestSchema, 'normal')
        print result
        return result
    
