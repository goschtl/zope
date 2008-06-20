##############################################################################
#
# Copyright (c) 2006-2007 Lovely Systems and Contributors.
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
"""
$Id$
"""
__docformat__ = "reStructuredText"

import os

from zope import interface
from zope import component
from zope import schema

from zope.component import zcml
from zope.component.zcml import handler
from zope.proxy import removeAllProxies
from zope.configuration.fields import GlobalObject, Tokens
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.security.zcml import Permission

from interfaces import IResponseCacheSettings, IPurge
from view import ResponseCacheSettings
from purge import PurgeUtil, PurgeDiskUtil

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('lovely.responseheader')


class ICacheSettingsDirective(interface.Interface):
    """Parameters for the cache settings directive."""

    for_ = GlobalObject(
            title = _(u'for'),
            description = _(u'The interface to register the settings for'),
            required = True,
            )

    layer = GlobalObject(
            title = _(u'Layer'),
            description = _(u'The layer for which the settings should be used'),
            required = False,
            default=IDefaultBrowserLayer,
            )

    class_ = GlobalObject(
            title = _(u'class'),
            description = _(u'The class to use for the settings'),
            required = False,
            )

    cacheName = schema.TextLine(
            title = _(u'Cachename'),
            required=False,
            default=u'',
            )

    key = schema.BytesLine(
            title = _(u'Cachekey'),
            required = False,
            )

    lifetime = schema.TextLine(
            title = _(u'Lifetime'),
            description = _(u"""
                The lifetime of the cache entry in seconds.
                The content of this filed will be evaluated. It is possible to
                give the value in the form '11*60*60'.
                """),
            required = False,
            default = None,
            )

    dependOnContext = schema.Bool(
            title = _(u'Depend On Context'),
            description = _("""
                The dependency will always contain the context of the view.
                """),
            required = False,
            default = False,
            )

    dependencies = Tokens(
        required=False,
        title = _(u'Dependencies'),
        description = _("""
        Simple string dependencies seperated by whitespace
        """),
        value_type=schema.BytesLine())

# Arbitrary keys and values are allowed to be passed to the viewlet.
ICacheSettingsDirective.setTaggedValue('keyword_arguments', True)

class FactoryCacheSettings(ResponseCacheSettings):

    _deps = []

    def __init__(self, context, request):
        super(FactoryCacheSettings, self).__init__(context, request)
        self.dependOnContext = False

    @apply
    def dependencies():
        def get(self):
            if self.dependOnContext:
                view = removeAllProxies(self.context)
                context = removeAllProxies(view.context)
                return self._deps + [context]
            return self._deps
        def set(self, value):
            self._deps = value

        return property(get, set)

class CacheSettingsFactory(object):

    def __init__(self, cacheName, key, lifetime, dependOnContext,
                 dependencies, kwords):
        self.cacheName = cacheName
        self.key = key
        self.lifetime = lifetime
        self.dependOnContext = dependOnContext
        self.dependencies = dependencies
        self.kwords = kwords

    def __call__(self, context, request):
        settings = FactoryCacheSettings(context, request)
        if self.cacheName is not None:
            settings.cacheName = self.cacheName
        if self.key is not None:
            settings.key = self.key
        if self.lifetime is not None:
            settings.lifetime = self.lifetime
        if self.dependencies is not None:
            settings._deps = self.dependencies
        settings.dependOnContext = self.dependOnContext
        for k, v in self.kwords.items():
            setattr(settings, k, v)
        return settings


def cacheSettingsDirective(_context,
                           for_,
                           layer=IDefaultBrowserLayer,
                           class_=None,
                           cacheName=None,
                           key=None,
                           lifetime=None,
                           dependOnContext=False,
                           dependencies = None,
                           **kwords
                          ):
    if class_:
        cdict = {}
        if lifetime is not None:
            cdict['lifetime'] = eval(lifetime)
        if cacheName is not None:
            cdict['cacheName'] = cacheName
        if key is not None:
            cdict['key'] = key
        if dependOnContext is not None:
            cdict['dependOnContext'] = dependOnContext
        if dependencies is not None:
            cdict['dependencies'] = dependencies
        cdict.update(kwords)
        new_class = type(class_.__name__, (class_,), cdict)
    else:
        if lifetime is not None:
            lifetime=eval(lifetime)
        new_class = CacheSettingsFactory(
                cacheName, key, lifetime, dependOnContext,
                dependencies, kwords)
    _context.action(
        discriminator = (
            'cacheSettings',
            layer,
            for_,
            ),
        callable = handler,
        args = ('registerAdapter',
                new_class,
                (for_, layer),
                IResponseCacheSettings,
                '',
                _context.info),
        )



class IPurgeDirective(interface.Interface):
    """Parameters for the purge directive."""

    hosts = Tokens(
        title=u'Hosts',
        description=u'Lists of hosts to get purged',
        required=True,
        value_type=schema.URI(title=u"host"))

    timeout = schema.Int(
        title = _(u'Timeout'),
        description=u'Timeout for purge requests in seconds. Keep it short!',
        required=True,
        )

    retryDelay = schema.Int(
        title = _(u'Cachename'),
        description=u'Retry delay to purge after a timeout in seconds.',
        required=True,
        )

    permission = Permission(
        title=_("Permission"),
        description=_("Permission required to use this component."),
        required=False,
        )


def purgeDirective(_context, hosts, timeout, retryDelay, permission=None):
    """Function to create a perge utility"""

    util = PurgeUtil(hosts, timeout, retryDelay)
    zcml.utility(_context,
                 provides=IPurge,
                 component=util,
                 permission=permission,
                 name='')


class IPurgeDiskDirective(interface.Interface):
    """Parameters for the purge disk directive."""

    paths = Tokens(
        title=u'Paths',
        description=u'Lists of paths where to execute purge expressions',
        required=True,
        value_type=schema.TextLine(title=u"path"))

    permission = Permission(
        title=_("Permission"),
        description=_("Permission required to use this component."),
        required=False,
        )


def purgeDiskDirective(_context, paths, permission=None):
    """Function to create a purge disk utility"""

    util = PurgeDiskUtil(paths)
    zcml.utility(_context,
                 provides=IPurge,
                 component=util,
                 permission=permission,
                 name='disk')


