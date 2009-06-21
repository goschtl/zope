##############################################################################
#
# Copyright Zope Foundation and Contributors.
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

import os
import zope.app.publication.browser
import zope.app.publication.traversers
import zope.component
import zope.configuration.xmlconfig
import zope.interface
import zope.location.interfaces
import zope.publisher.interfaces.browser
import zope.publisher.paste

class Publication(zope.app.publication.browser.BrowserPublication):

    def __init__(self, DEFAULT=None, **options):
        if DEFAULT:
            DEFAULT = DEFAULT.copy()
            DEFAULT.update(options)
            options = DEFAULT

        super(Publication, self).__init__(None)

        root = options.get('root')
        if root is None:
            rootobj = zope.location.Location()
            zope.interface.directlyProvides(
                rootobj, zope.location.interfaces.IRoot)
            root = lambda request: rootobj
        elif root.startswith('egg:'):
            root = zope.publisher.paste.get_egg(root[4:], 'zc.publication.root')
        else:
            module_name, expr = root.split(':', 1)
            module = __import__(module_name, {}, {}, ['*'])
            root = eval(expr, module.__dict__, options)

        self.getApplication = lambda request: self.proxy(root(request))

        zcml = options.get('zcml', '<include package="zc.publication" />')
        zope.configuration.xmlconfig.string(zcml)

        logconfig = options.get('loggers')
        if logconfig:
            import ZConfig
            ZConfig.configureLoggers(logconfig)
        else:
            import logging
            logging.basicConfig()

    def proxy(self, ob):
        return ob

class Application(zope.publisher.paste.Application):

    def __init__(self, global_config=None, **options):
        zope.publisher.paste.Application.__init__(
            self, global_config, 'egg:zc.publication', **options)

class DefaultTraverser(
    zope.app.publication.traversers.SimpleComponentTraverser,
    ):

    def browserDefault(self, request):
        return self.context, ()
