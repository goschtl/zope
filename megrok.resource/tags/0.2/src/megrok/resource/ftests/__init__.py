# -*- coding: utf-8 -*-

import os.path
import megrok.resource
import grokcore.view as view
from megrok.resource import Library
from zope.app.testing.functional import ZCMLLayer

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer', allow_teardown=True)

class SomeCSS(Library):
    view.path('ftests/css')
