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

from zope.app.session.interfaces import IClientId, IClientIdManager, ISession
from zope.app.session.interfaces import ISessionDataContainer
from zope.app.session.session import PersistentSessionDataContainer
from zope.app.session.interfaces import ISessionPkgData, ISessionData
from zope.app.session.session import ClientId, Session
from zope.app.session.http import CookieClientIdManager
from zope.publisher.interfaces import IRequest

from z3c.authentication.cookie.session import LifeTimeSession
from z3c.authentication.cookie.interfaces import (ILifeTimeClientId,
                                                  ILifeTimeSession)
from z3c.authentication.simple.principal import AuthenticatedPrincipal
from z3c.authentication.simple.principal import FoundPrincipal
from z3c.authentication.simple.interfaces import (IAuthenticatedPrincipal,
                                                 IFoundPrincipal)

import grok
from martian.interfaces import IModuleInfo
import tfws.website

ftesting_zcml = os.path.join(
    os.path.dirname(tfws.website.__file__), 'ftesting.zcml')
TestLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer')

def printElement(browser, xpath, multiple=False, serialize=True):
    """Print method from z3c.form to use with z3c.etestbrowser"""
    result = [serialize and lxml.etree.tounicode(elem) or elem
              for elem in browser.etree.xpath(xpath)]
    if not multiple:
        print result[0]
        return
    for elem in result:
        print elem

class ModuleInfo(object):
    """Dummy module info for martians"""
    zope.interface.implements(IModuleInfo)
    path = tfws.website.__file__
    package_dotted_name = 'tfws.website'

    def getAnnotation(self, name, default):
        return default

class TestClientId(object):
    zope.interface.implements(IClientId)
    def __new__(cls, request):
        return 'dummyclientidfortesting'

def setUp(test):
    root = setup.placefulSetUp(site=True)
    test.globs['root'] = root
    test.globs['module_info'] = ModuleInfo()
    ztapi.provideAdapter(IAnnotatable, IPrincipalRoleManager,
                            AnnotationPrincipalRoleManager)
    ztapi.provideAdapter(IAnnotatable, IRolePermissionManager,
                            AnnotationRolePermissionManager)
    metaconfigure.registerType('provider', tales.TALESProviderExpression)

    # testing setup borrowed from z3c.authentication.cookie testing
    # setup client ids
    ztapi.provideAdapter(IRequest, IClientId, TestClientId)
    ztapi.provideAdapter(IRequest, ILifeTimeClientId, TestClientId)

    # setup session adapters
    ztapi.provideAdapter(IRequest, ISession, Session)
    ztapi.provideAdapter(IRequest, ILifeTimeSession, LifeTimeSession)

    # setup session data containers
    #defaultSDC = PersistentSessionDataContainer()
    #ztapi.provideUtility(ISessionDataContainer, defaultSDC, '')

    # setup principal adapters
    zope.component.provideAdapter(AuthenticatedPrincipal, 
                   provides=IAuthenticatedPrincipal)
    zope.component.provideAdapter(FoundPrincipal, 
                   provides=IFoundPrincipal)


def tearDown(test):
    setup.placefulTearDown()

