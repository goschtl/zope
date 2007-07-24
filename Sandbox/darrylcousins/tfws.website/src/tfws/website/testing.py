import os.path
import lxml.etree

import zope.interface
from zope.app.testing.functional import ZCMLLayer
from zope.app.testing import setup, ztapi
from zope.app.pagetemplate import metaconfigure
from zope.contentprovider import tales

from zope.annotation.interfaces import IAnnotatable
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager
from zope.app.securitypolicy.interfaces import IRolePermissionManager
from zope.app.securitypolicy.principalrole \
     import AnnotationPrincipalRoleManager
from zope.app.securitypolicy.rolepermission \
     import AnnotationRolePermissionManager

import grok
from martian.interfaces import IModuleInfo
import tfws.website

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

class ModuleInfo(object):
    zope.interface.implements(IModuleInfo)
    path = tfws.website.__file__
    package_dotted_name = 'tfws.website'

    def getAnnotation(self, name, default):
        return default

def setUp(test):
    root = setup.placefulSetUp(site=True)
    test.globs['root'] = root
    test.globs['module_info'] = ModuleInfo()
    ztapi.provideAdapter(IAnnotatable, IPrincipalRoleManager,
                            AnnotationPrincipalRoleManager)
    ztapi.provideAdapter(IAnnotatable, IRolePermissionManager,
                            AnnotationRolePermissionManager)
    metaconfigure.registerType('provider', tales.TALESProviderExpression)

def tearDown(test):
    setup.placefulTearDown()

