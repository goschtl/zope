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


def _check_princexml():

    status, output = runcmd('prince --help')
    return status == 0

princexml_available = _check_princexml()

class PrinceXMLConverter(object):

    implements(IFOConverter)

    def convert(self, html_filename, output_filename=None):
        """ Convert a HTML file to PDF using PrinceXML"""

        if not output_filename:
            output_filename = newTempfile(suffix='.pdf')

        if sys.platform == 'win32':
            raise NotImplementedError('No support for PrinceXML on Windows')
        else:
            cmd = 'prince "%s" "%s"' % (html_filename, output_filename)

        status, output = runcmd(cmd)
        if status != 0:
            raise RuntimeError('Error executing: %s' % cmd)

        return output_filename

if __name__ == '__main__':
    print _check_princexml()
