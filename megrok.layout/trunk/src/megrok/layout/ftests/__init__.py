# -*- coding: utf-8 -*-

import os.path
from zope.app.testing.functional import ZCMLLayer
from zope.configuration.config import ConfigurationMachine
from grokcore.component import zcml


ftesting_zcml = os.path.join(
    os.path.dirname(__file__), 'ftesting.zcml')

FunctionalLayer = ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer', allow_teardown=True)


def grok(module_name):
    config = ConfigurationMachine()
    zcml.do_grok('grokcore.component.meta', config)
    zcml.do_grok('grokcore.security.meta', config)
    zcml.do_grok('grokcore.view.meta', config)
    zcml.do_grok('grokcore.view.templatereg', config)
    zcml.do_grok(module_name, config)
    config.execute_actions()
