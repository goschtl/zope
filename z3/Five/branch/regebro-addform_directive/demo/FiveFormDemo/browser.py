from Products.Five import BrowserView

from zope.app.form.utility import setUpWidgets, getWidgetsData
from zope.schema import getFieldNamesInOrder
from zope.app.form.interfaces import IInputWidget

from contact import ISimpleContact

class SimpleFormView(BrowserView):
    """More docstring. Please Zope"""

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

        setUpWidgets(self, ISimpleContact, IInputWidget)

    def simpleForm(self):
        """www"""
        result=''
        result+='<form action="formSubmit" method="post">'
        for widget in self.getWidgets():
            result+=widget.label+': <br/>'+widget()+'<br/>\n'
        result+='<input type="submit" name="submit" value="submit"/>'
        result+='</form>'

        return result;

    def formSubmit(self):
        """www"""
        data = getWidgetsData(self, ISimpleContact)
        return "<html><body>The data you entered:<br/>"+str(data)+"</body></html>"

    def getWidgets(self):
        return ([getattr(self, name+'_widget')
                 for name in getFieldNamesInOrder(ISimpleContact)]
                )
