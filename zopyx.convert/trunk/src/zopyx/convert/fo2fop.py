##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import sys

from util import newTempfile, runcmd
from logger import LOG

from zope.interface import implements
from interfaces import IFOConverter

fop_home = os.environ.get('FOP_HOME')

def _check_fop():
    if not fop_home:
        LOG.debug('$FOP_HOME not set')
        return False

    if not os.path.exists(fop_home):
        LOG.debug('$FOP_HOME=%s does not exist' % fop_home)
        return False

    return True

fop_available = _check_fop()

class FOPPDFConverter(object):

    implements(IFOConverter)

    def convert(self, fo_filename, output_filename=None):
        """ Convert a FO file to PDF using FOP"""

        if not output_filename:
            output_filename = newTempfile(suffix='.pdf')

        if sys.platform == 'win32':
            cmd = '%s\\fop.bat -fo "%s" -pdf "%s"' % (fop_home, fo_filename, output_filename)
        else:
            cmd = 'sh "%s/fop" -fo "%s" -pdf "%s"' % (fop_home, fo_filename, output_filename)

        status, output = runcmd(cmd)
        if status != 0:
            raise RuntimeError('Error executing: %s' % cmd)

        return output_filename

