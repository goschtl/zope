# -*- coding: utf-8 -*-
import os
from zope.app.testing.functional import ZCMLLayer

ftesting_zcml = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)), 'ftesting.zcml')

GrokCodeBrowserFunctionalLayer = ZCMLLayer(
    ftesting_zcml, __name__,
    'GrokCodeBRowserFunctionalLayer', allow_teardown=True)
