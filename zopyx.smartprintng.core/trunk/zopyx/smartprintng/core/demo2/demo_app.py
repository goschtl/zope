##########################################################################
# zopyx.smartprintng.core - High-quality export of Zope content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


import os
from zope.interface import Interface, implements

# initialize/register all HTML transformations
import zopyx.smartprintng.core.transformation
from zopyx.smartprintng.core.highlevel import convert
from zopyx.smartprintng.core.interfaces import IImageFetcher
from zopyx.smartprintng.core.adapters import ExternalImageFetcher


from zopyx.smartprintng.core.renderer import Renderer
from zopyx.smartprintng.core.interfaces import IImageFetcher
from zopyx.smartprintng.core.adapters import ExternalImageFetcher


# register resources directory for demo purposes 
from zopyx.smartprintng.core import resources

def demo_convert(fullname, orientation='horizontal', debug=False):
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

    css = orientation == 'horizontal' and 'business_card.css' or  'business_card2.css'
    orientation_ext = orientation=='horizontal' and '_landscape' or '_upside'
    styles = debug and [css, 'debug.css'] or [css]
    ext = debug and '_debug' or ''

    context = TestContent()
    result = convert(context=context,
                     html='',
                     styles=styles,
                     resource_name='demo',
                     converter='pdf-prince',
                     template_options=dict(fullname=fullname),
                     destination_filename=os.path.join(os.getcwd(), 
                                                       '%s%s%s.pdf' % (fullname, orientation_ext, ext)),
                    )

    return os.path.abspath(result)

if __name__ == '__main__':

    for fullname in ('Andreas Jung', 'Heinz Becker', 'Hilde Becker'):
        for orientation in ('horizontal', 'vertical'):
            filename = demo_convert(fullname, orientation)
            print fullname, orientation, filename
