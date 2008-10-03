##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import sys

from util import newTempfile, runcmd, which, win32, checkEnvironment
from logger import LOG

from zope.interface import implements
from interfaces import IFOConverter

xfc_dir = os.environ.get('XFC_DIR')

def _check_xfc():
    if not checkEnvironment('XFC_DIR'):
        return False
    return True


def fo2xfc(fo_filename, format='rtf', output_filename=None):
    """ Convert a FO file to some format support 
        through XFC-4.0.
    """

    if not format in ('rtf', 'docx', 'wml', 'odt'):
        raise ValueError('Unsupported format: %s' % format)

    if not output_filename:
        output_filename = newTempfile(suffix='.%s' % format)

    if sys.platform == 'win32':
        cmd = '"%s\\fo2%s.bat"  "%s" "%s"' % (xfc_dir, format, fo_filename, output_filename) 
    else:	
        cmd = '"%s/fo2%s" "%s" "%s"' % (xfc_dir, format, fo_filename, output_filename)

    status, output = runcmd(cmd)
    if status != 0:
        raise RuntimeError('Error executing: %s' % cmd)

    return output_filename


class RTFConverter(object):

    implements(IFOConverter)
    def convert(self, fo_filename, output_filename=None):
        return fo2xfc(fo_filename, 'rtf', output_filename)

class ODTConverter(object):

    implements(IFOConverter)
    def convert(self, fo_filename, output_filename=None):
        return fo2xfc(fo_filename, 'odt', output_filename)

class WMLConverter(object):

    implements(IFOConverter)
    def convert(self, fo_filename, output_filename=None):
        return fo2xfc(fo_filename, 'wml', output_filename)

class DOCXConverter(object):

    implements(IFOConverter)
    def convert(self, fo_filename, output_filename=None):
        return fo2xfc(fo_filename, 'docx', output_filename)

xfc_available = _check_xfc()
