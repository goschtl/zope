##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Sample generator for principals

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.event
import zope.schema
import zope.lifecycleevent
from zope.interface import implements
from zope.security.proxy import removeSecurityProxy
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication import principalfolder
from zope.app.component import hooks

from lovely.sampledata.interfaces import ISampleDataPlugin

from lovely.sampledata.data import DataGenerator

from lovely.sampledata import _


class ISamplePrincipalParameters(zope.interface.Interface):
    """The parameters for the sample principal generator."""

    minPrincipals = zope.schema.Int(
            title = _(u'Min principals'),
            description = _(u'Create at least this number of pricipals from'
                            u' the principals file.\n'
                            u'This has higher priority than maxPricipals.\n'
                            u'-1 : create all principals from the file.'
                           ),
            required = False,
            default = -1,
            )

    maxPrincipals = zope.schema.Int(
            title = _(u'Max principals'),
            description = _(u'The maximum number of principals to create.'),
            required = False,
            default = -1,
            )

    pauLocation = zope.schema.TextLine(
            title = _(u'PAU location'),
            description = _(u'Path to the PAU inside the site manager.'),
            required = False,
            default = u'default/pau',
            )


class SamplePrincipals(object):

    implements(ISampleDataPlugin)

    name = 'lovely.principals'
    dependencies = []
    schema = ISamplePrincipalParameters

    maxPrincipals = None
    minPrincipals = None

    def generate(self, context, param={}, seed=None):
        """Generate sample pricipals"""
        self.minPrincipals = int(param['minPrincipals'])
        if self.minPrincipals<0:
            self.minPrincipals = None
        self.maxPrincipals = int(param['maxPrincipals'])
        if self.maxPrincipals<0:
            self.maxPrincipals = None
        originalSite = hooks.getSite()
        hooks.setSite(context)
        sm = zope.component.getSiteManager(context)
        self.pau = sm
        for loc in param['pauLocation'].split('/'):
            self.pau = self.pau[loc]

        numCreated = 0
        self.logins = []
        generator = DataGenerator(str(seed) + self.name)
        principals = generator.readCSV('testprincipals.txt')
        for info in principals:
            if (    self.maxPrincipals is not None
                and numCreated>=self.maxPrincipals):
                break
            login = unicode(info[1])
            if login in self.logins:
                # ignore duplicate principals
                continue
            self._createPrincipal(info)
            numCreated+=1

        if (    self.minPrincipals is not None
            and numCreated<self.minPrincipals):
            for i in range(self.minPrincipals-numCreated):
                info = ['group','login%i'%i,'name%i'%i,'%i'%i]
                self._createPrincipal(info)

        hooks.setSite(originalSite)

    def _createPrincipal(self, info):
        login = unicode(info[1])
        self.logins.append(login)
        if login in self.pau['members']:
            return
        groupId = unicode(info[0])
        name = unicode(info[2])
        password = unicode(info[3])
        principal = principalfolder.InternalPrincipal(login,
                            password, name, passwordManagerName="SHA1")
        zope.event.notify(
            zope.lifecycleevent.ObjectCreatedEvent(principal))
        self.pau['members'][login] = principal

