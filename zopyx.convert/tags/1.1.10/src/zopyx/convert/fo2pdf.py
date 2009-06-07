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

xinc_home = os.environ.get('XINC_HOME')

def _check_xinc():
    if not xinc_home:
        LOG.debug('$XINC_HOME not set')
        return False

    if not os.path.exists(xinc_home):
        LOG.debug('$XINC_HOME=%s does not exist' % xinc_home)
        return False

    return True        

xinc_available = _check_xinc()

class PDFConverter(object):

    implements(IFOConverter)

    def convert(self, fo_filename, output_filename=None):
        """ Convert a FO file to PDF using XINC """

        if not output_filename:
            output_filename = newTempfile(suffix='.pdf')

        if sys.platform == 'win32':
            cmd = '%s\\xinc.exe -fo "%s" -pdf "%s"' % (xinc_home, fo_filename, output_filename)
        else:
            cmd = '"%s/bin/unix/xinc" -fo "%s" -pdf "%s"' % (xinc_home, fo_filename, output_filename)

        status, output = runcmd(cmd)
        if status != 0:
            raise RuntimeError('Error executing: %s' % cmd)

        return output_filename

