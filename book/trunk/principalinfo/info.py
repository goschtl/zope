##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Principal Information Implementation

$Id$
"""
from persistent.dict import PersistentDict
from zope.interface import implements
from zope.app import zapi

from interfaces import IPrincipalInformation

key = 'book.principalinfo.Information'

class PrincipalInformation(object):
    r"""Principal Information Adapter

    Here is a small demonstration on how it works.

    Do the tedious setup first.

    >>> from zope.app.tests import setup
    >>> from zope.app.principalannotation.interfaces import \
    ...      IPrincipalAnnotationService
    >>> from zope.app.principalannotation import PrincipalAnnotationService

    >>> site = setup.placefulSetUp(site=True)
    >>> sm = zapi.getGlobalServices()
    >>> sm.defineService('PrincipalAnnotation',
    ...                  IPrincipalAnnotationService)
    >>> svc = setup.addService(site.getSiteManager(), 'PrincipalAnnotation',
    ...                        PrincipalAnnotationService())

    Let's now test the principal annotation. To do this, we need a
    minimalistic principal.

    >>> class Principal(object):
    ...     id = 'user1'
    >>> principal = Principal()

    Now create the adapter using the principal and make sure that the values
    are initially unset.

    >>> info = PrincipalInformation(principal)
    >>> info.email is None
    True
    >>> info.ircNickname is None
    True
    >>> info.phone
    Traceback (most recent call last):
    ...
    AttributeError: 'phone' not in interface.
    
    Now set the `email` field and make sure it is still there, even if the
    adapter is regenerated.

    >>> info.email = 'foo@bar.com'
    >>> info.email
    'foo@bar.com'

    >>> info = PrincipalInformation(principal)
    >>> info.email
    'foo@bar.com'

    Now make really sure that the service stores the data.

    >>> svc.annotations['user1']['book.principalinfo.Information']['email']
    'foo@bar.com'

    >>> setup.placefulTearDown()
    """
    implements(IPrincipalInformation)

    def __init__(self, principal):
        annotationsvc = zapi.getService('PrincipalAnnotation')
        annotations = annotationsvc.getAnnotations(principal)
        if annotations.get(key) is None:
            annotations[key] = PersistentDict()
        self.info = annotations[key]

    def __getattr__(self, name):
        if name in IPrincipalInformation:
            return self.info.get(name, None)
        raise AttributeError, "'%s' not in interface." %name

    def __setattr__(self, name, value):
        if name in IPrincipalInformation:
            self.info[name] = value
        else:
            super(PrincipalInformation, self).__setattr__(name, value)
