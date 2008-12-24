##########################################################################
# zopyx.convert2 - SmartPrintNG low-level functionality
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import re

from util import newTempfile
from htmlentitydefs import name2codepoint
from BeautifulSoup import BeautifulSoup

def tidyhtml(filename, encoding='utf-8'):

    html = file(filename, 'rb').read()

    # use BeautifulSoup for performing HTML checks
    # and conversion to XHTML
    soup = BeautifulSoup(html)

    # check if all image files exist
    for img in soup.findAll('img'):
        src = img['src']
        if not os.path.exists(src):
            raise IOError('No image file found: %s' % src)

    html = soup.renderContents()

    # replace the HTML tag
    html = '<html xmlns="http://www.w3.org/1999/xhtml">' + \
            html[html.find('<html') + 6:]
    # add the XML preamble
    html = '<?xml version="1.0" ?>\n' + html

    # replace all HTML entities with numeric entities
    def handler(mo):
        """ Callback to convert entities """
        e = mo.group(1)
        v = e[1:-1]
        if not v.startswith('#'):
            codepoint =  name2codepoint.get(v)
            return codepoint and '&#%d;' % codepoint or ''
        else:
            return e
    
    entity_reg = re.compile('(&.*?;)')
    html = entity_reg.sub(handler, html)

    filename = newTempfile()
    file(filename, 'wb').write(str(html))
    return filename

