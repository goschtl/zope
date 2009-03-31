import os.path
import megrok.ootbviewlets
from zope.app.testing.functional import ZCMLLayer

ftesting_zcml = os.path.join(os.path.dirname(megrok.ootbviewlets.__file__), 
                             'ftesting.zcml')
FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer',
                            allow_teardown=True)

