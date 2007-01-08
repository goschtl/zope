from Products.Five import BrowserView
from zope.security.management import checkPermission

class Zope3SecurityView(BrowserView):

    def __call__(self):
        if checkPermission('zope2.View', self.context):
            return "Yes, you have the zope2.View permission."
        else:
            return "No, you don't have the zope2.View permission."
