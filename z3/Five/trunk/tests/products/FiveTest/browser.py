from Products.Five.api import BrowserView

class SimpleContentView(BrowserView):
    """More docstring. Please Zope"""

    def eagle(self):
        """Docstring"""
        return "The eagle has landed"

    def mouse(self):
	"""Docstring"""
	return "The mouse has been eaten by the eagle"""

    def no_doc_string(self):
	return "No docstring"
