from Products.Five import BrowserView
from Products.Five import StandardMacros as BaseMacros

class SimpleContentView(BrowserView):
    """More docstring. Please Zope"""

    def eagle(self):
        """Docstring"""
        return "The eagle has landed"

    def mouse(self):
        """Docstring"""
        return "The mouse has been eaten by the eagle"

class FancyContentView(BrowserView):
    """Fancy, fancy stuff"""

    def view(self):
        return "Fancy, fancy"

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

class NewStyleClass(object):
    """
    This is a testclass to verify that new style classes are ignored
    in browser:page
    """

    def __init__(self, context, request):
        """Docstring"""
        self.context = context
        self.request = request

    def method(self):
        """Docstring"""
        return

class StandardMacros(BaseMacros):

    macro_pages = ('bird_macros', 'dog_macros')
    aliases = {'flying':'birdmacro',
               'walking':'dogmacro'}
