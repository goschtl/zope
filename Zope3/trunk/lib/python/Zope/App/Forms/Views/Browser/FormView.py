from Zope.Publisher.Browser.BrowserView import BrowserView
from Interface import Interface
from Schema.IField import IField
from Zope.ComponentArchitecture import getView

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
    
    
