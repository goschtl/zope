# Copyright (c) 2007-2010 Zope Foundation and Contributors
# See also LICENSE.txt
import os.path
import megrok.kss
from zope.app.testing.functional import ZCMLLayer

integration_zcml = os.path.join(
    os.path.dirname(megrok.kss.__file__), 'integration.zcml')
IntegrationLayer = ZCMLLayer(integration_zcml, __name__, 'IntegrationLayer')
