import os.path
import megrok.resource

from zope.app.testing.functional import ZCMLLayer
ftesting_zcml = os.path.join(os.path.dirname(megrok.resource.__file__),
                             'ftesting.zcml')
FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer',
                            allow_teardown=True)

