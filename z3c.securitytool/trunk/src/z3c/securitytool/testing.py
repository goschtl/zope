
import os
from zope.app.testing import functional

SecurityToolLayer = functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'SecuritiyToolLayer', allow_teardown=True)

