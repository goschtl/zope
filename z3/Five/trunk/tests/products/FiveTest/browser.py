from Products.Five.api import BrowserView

class SimpleContentView(BrowserView):
    """More docstring. Please Zope"""

    def eagle(self):
        """Docstring"""
        return "The eagle has landed"

    def mouse(self):
        """Docstring"""
        return "The mouse has been eaten by the eagle"

class CallableNoDocstring:

    def __call__(self):
        return "No docstring"

def function_no_docstring(self):
    return "No docstring"

class NoDocstringView(BrowserView):

    def method(self):
        return "No docstring"

    function = function_no_docstring

    object = CallableNoDocstring()
