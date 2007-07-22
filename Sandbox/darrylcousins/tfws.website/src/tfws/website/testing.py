import os.path
import lxml.etree

import tfws.website
from zope.app.testing.functional import ZCMLLayer

ftesting_zcml = os.path.join(
    os.path.dirname(tfws.website.__file__), 'ftesting.zcml')
TestLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer')

def printElement(browser, xpath, multiple=False, serialize=True):
    result = [serialize and lxml.etree.tounicode(elem) or elem
              for elem in browser.etree.xpath(xpath)]
    if not multiple:
        print result[0]
        return
    for elem in result:
        print elem

