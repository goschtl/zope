from zope.interface import implements
from zope.component import queryUtility
from Products.Five.security.interfaces import IPermission

CheckerPublic = 'zope.Public'
CheckerPrivate = 'zope.Private'

def getSecurityInfo(klass):
    sec = {}
    info = vars(klass)
    if info.has_key('__ac_permissions__'):
        sec['__ac_permissions__'] = info['__ac_permissions__']
    for k, v in info.items():
        if k.endswith('__roles__'):
            sec[k] = v
    return sec

def checkPermission(context, permission_id):
    """Check whether a given permission exists in the provided context.

    >>> from zope.app.tests.placelesssetup import setUp, tearDown
    >>> setUp()

    >>> from zope.app.tests.ztapi import provideUtility
    >>> provideUtility(IPermission, Permission('x'), 'x')

    >>> checkPermission(None, 'x')
    >>> checkPermission(None, 'y')
    Traceback (most recent call last):
    ...
    ValueError: ('Undefined permission id', 'y')

    >>> tearDown()
    """
    if permission_id == CheckerPublic:
        return
    if not queryUtility(IPermission, permission_id, context=context):
        raise ValueError("Undefined permission id", permission_id)

class Permission(object):
    implements(IPermission)

    def __init__(self, id, title="", description=""):
        self.id = id
        self.title = title
        self.description = description
