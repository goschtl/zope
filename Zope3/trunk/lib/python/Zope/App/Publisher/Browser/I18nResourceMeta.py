##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""Browser configuration code

$Id: I18nResourceMeta.py,v 1.1 2002/06/25 14:30:08 mgedmin Exp $
"""

from Zope.Security.Proxy import Proxy
from Zope.Security.Checker \
     import CheckerPublic, NamesChecker, Checker

from Zope.Configuration.Action import Action
from Zope.Configuration.Exceptions import ConfigurationError

from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation

from Zope.App.ComponentArchitecture.metaConfigure import handler

from Zope.App.Publisher.FileResource import File, Image
from Zope.App.Publisher.Browser.I18nFileResource \
     import I18nFileResourceFactory

class I18nResource(object):

    type = IBrowserPresentation
    default_allowed_attributes = '__call__'

    def __init__(self, _context, name=None, defaultLanguage='en',
                 layer='default', permission=None):
        self.name = name
        self.defaultLanguage = defaultLanguage
        self.layer = layer
        self.permission = permission
        self.__data = {}


    def translation(self, _context, language, file=None, image=None):

        if file is not None and image is not None:
            raise ConfigurationError(
                "Can't use more than one of file, and image "
                "attributes for resource directives"
                )
        elif file is not None:
            self.__data[language] = File(_context.path(file))
        elif image is not None:
            self.__data[language] = Image(_context.path(image))
        else:
            raise ConfigurationError(
                "At least one of the file, and image "
                "attributes for resource directives must be specified"
                )

        return ()


    def __call__(self, require = None):
        if self.name is None:
            return ()

        permission = self.permission
        factory = I18nFileResourceFactory(self.__data, self.defaultLanguage)

        if permission:
            if require is None:
                require = {}

            if permission == 'Zope.Public':
                permission = CheckerPublic

        if require:
            checker = Checker(require.get)

            factory = self._proxyFactory(factory, checker)

        return [
            Action(
                discriminator = ('i18n-resource', self.name, self.type,
                                 self.layer),
                callable = handler,
                args = ('Resources', 'provideResource', self.name, self.type,
                        factory, self.layer)
                )
            ]


    def _proxyFactory(self, factory, checker):
        def proxyView(request,
                      factory=factory, checker=checker):
            resource = factory(request)

            # We need this in case the resource gets unwrapped and
            # needs to be rewrapped 
            resource.__Security_checker__ = checker

            return Proxy(resource, checker)

        return proxyView
