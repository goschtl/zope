#prini#########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import sys

from convert import BaseConverter
from util import runcmd, which, win32, checkEnvironment, newTempfile
from logger import LOG

from tidy import tidyhtml

def _check_prince():
    if not which('prince'):
        return False
    return True

prince_available = _check_prince()

def html2pdf(html_filename, output_filename=None, **prince_options):
    """ Convert a HTML file to PDF using FOP"""

    if not output_filename:
        output_filename = newTempfile(suffix='.pdf')

    if not prince_available:
        raise RuntimeError("The external PrinceXML converter isn't available")

    options = list()
    for k,v in prince_options.items():
        if v is None:
            options.append('--%s ' % k)
        else:
            options.append('--%s="%s" ' % (k, v)) 

    if sys.platform == 'win32':
        raise NotImplementedError('No support for PrinceXML on Windows available')
    else:
        cmd = 'sh "prince" "%s" %s -o "%s"' % (html_filename, ' '.join(options), output_filename)
    
    status, output = runcmd(cmd)
    if status != 0:
        raise RuntimeError('Error executing: %s' % cmd)
    return output_filename


class HTML2PDF(BaseConverter):

    name = 'pdf-prince'
    output_format = 'pdf'
    visible_name = 'PDF (PrinceXML)'
    visible = True

    @staticmethod
    def available():
        return prince_available

    def convert(self, output_filename=None, **prince_options):
        tidy_filename = tidyhtml(self.filename, self.encoding)
        output_filename = html2pdf(tidy_filename, output_filename, **prince_options)
        os.unlink(tidy_filename)
        return output_filename


from registry import registerConverter
registerConverter(HTML2PDF)

if __name__ == '__main__':
    print html2pdf(sys.argv[1], 'out.pdf', **{'encrypt' : None,
                                              'disallow-print' : None,
                                              'disallow-copy' : None,
                                              'disallow-modify' : None,
                                              'owner-password' : 'foo1',
                                              'user-password' : 'foo'})
