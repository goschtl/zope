##########################################################################
# zopyx.smartprintng.core - High-quality export of Zope content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


import os

# initialize/register all HTML transformations
import zopyx.smartprintng.core.transformation
from zopyx.smartprintng.core.highlevel import convert

from zope.interface import Interface, implements


class ITestContent(Interface):
    pass

class TestContent(object):
    implements(ITestContent)

html = file(os.path.join(os.path.dirname(__file__), 'demo.html')).read()

# register resources directory for demo purposes 
from zopyx.smartprintng.core import resources

def main():
    resources_configuration_file = os.path.join(os.path.dirname(__file__), 'resources', 'resources.ini')
    resources.registerResource(ITestContent, resources_configuration_file)

    from zopyx.convert2.registry import availableConverters

    for c in availableConverters():

        print 'Converter: %s' % c
        context = TestContent()
        result = convert(context=context,
                         html=html,
                         aggregator_name='foo',
                         styles=['fop_styles.css', 'demo_styles.css'],
                         transformations=['zopyx.smartprintng.imageremover', 'zopyx.smartprintng.pagebreaker'],
                         resource_name='demo',
                         converter=c,
                        )
                        
        print 'Generated:', os.path.abspath(result)
        print

if __name__ == '__main__':
    import sys
    sys.exit(main())
