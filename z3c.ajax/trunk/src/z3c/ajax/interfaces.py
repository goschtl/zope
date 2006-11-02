from zope import interface
from zope.app.form.interfaces import IInputWidget, IDisplayWidget


class IAjaxTraverser(interface.Interface):

    """an ajax traverser"""

class IAjaxWidget(interface.Interface):

    """an ajax widget, which is actualy a browser page"""

class IAjaxFormTraverser(interface.Interface):

    """a traverser that traverses to widgets of a form"""

class IAjaxWidgetTraverser(interface.Interface):

    """a traverser that traverses to displays of a widget"""

class IAjaxForm(IInputWidget):

    def __call__(self):
        """default view"""

    def renderDisplay():

        """render display view"""

    def renderInput():

        """render input view"""

    def browserDefault():

        """ """
