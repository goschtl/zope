from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_gzo_policy():
    "Set up the additional products required for the Grok site"
    fiveconfigure.debug_mode = True
    import gzo.plonepolicy
    zcml.load_config('configure.zcml',
                     gzo.plonepolicy)
    fiveconfigure.debug_mode = False

    ztc.installPackage('gzo.plonepolicy')
    ztc.installProduct('gzo.plonesmashtheme')

setup_gzo_policy()
ptc.setupPloneSite(products=['gzo.plonepolicy'])

class GzoPolicyTestCase(ptc.PloneTestCase):
    "Base class for tests"
