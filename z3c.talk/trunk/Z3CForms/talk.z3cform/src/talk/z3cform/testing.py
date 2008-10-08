import os
from zope.app.testing.functional import ZCMLLayer

Z3CFormLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'Z3CFormLayer', allow_teardown=True)
