#
# This file is necessary to make this directory a package.

##############################################################################
# BBB: backward-comptibility; 12/18/2004

import sys
from zope.deprecation.deprecation import DeprecatedModule 
import zope.app

def deprecate(module):
    return DeprecatedModule(module,
                            'Test setup code moved from zope.app.tests to '
                            'zope.app.testing. This will go away in Zope 3.3.')


from zope.app.testing import placelesssetup
sys.modules['zope.app.tests.placelesssetup'] = deprecate(placelesssetup)
from zope.app.testing import setup
sys.modules['zope.app.tests.setup'] = deprecate(setup)
from zope.app.testing import dochttp
sys.modules['zope.app.tests.dochttp'] = deprecate(dochttp)
from zope.app.testing import functional
sys.modules['zope.app.tests.functional'] = deprecate(functional)
from zope.app.testing import test
sys.modules['zope.app.tests.test'] = deprecate(test)
from zope.app.testing import ztapi
sys.modules['zope.app.tests.ztapi'] = deprecate(ztapi)
#############################################################################
