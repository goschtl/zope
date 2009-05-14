##########################################################################
# zopyx.smartprintng.core - High-quality export of Zope content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


import os
from zope.interface import implements, Interface

# register resources directory for demo purposes 
from zopyx.smartprintng.core.highlevel import convert
from zopyx.smartprintng.core import resources
from zopyx.smartprintng.core.interfaces import IImageFetcher
from zopyx.smartprintng.core.adapters import ExternalImageFetcher

package_home = os.path.dirname(__file__)

def demo_convert():
    from zope.app.testing import ztapi

    class ITestContent(Interface):
        pass

    class TestContent(object):
        implements(ITestContent)

    try:
        ztapi.provideAdapter(ITestContent, IImageFetcher, ExternalImageFetcher)
    except:
        pass

    resources_configuration_file = os.path.join(os.path.dirname(__file__), 'resources', 'resources.ini')
    resources.registerResource(ITestContent, resources_configuration_file)


    filename = convert(context=TestContent(), html='', resource_name='demo', converter='pdf-prince')
    return filename        

if __name__ == '__main__':

    filename = demo_convert()
    print filename
