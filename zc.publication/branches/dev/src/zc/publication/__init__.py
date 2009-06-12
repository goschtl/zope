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
import zope.publisher.paste

class Publication(zope.app.publication.browser.BrowserPublication):

    def __init__(self, DEFAULT=None, **options):
        if DEFAULT:
            DEFAULT = DEFAULT.copy()
            DEFAULT.update(options)
            options = DEFAULT

        super(Publication, self).__init__(None)

        root = options['root']
        if root.startswith('egg:'):
            root = zope.publisher.paste.get_egg(root[4:], 'zc.publication.root')
            base = os.getcwd()         # XXX
        else:
            module_name, expr = root.split(':')
            module = __import__(module_name, {}, {}, ['*'])
            root = eval(expr, options, module.__dict__)
            base = os.path.dirname(module.__file__)

        self.getApplication = root

        zcml = options.get('zcml')
        if zcml is not None:
            zcml = os.path.join(base, zcml)
            import zope.configuration.xmlconfig
            zope.configuration.xmlconfig.xmlconfig(open(zcml))

        logconfig = options.get('logging')
        if logconfig:
            import ZConfig
            ZConfig.configureLoggers(logconfig)
        else:
            import logging
            logging.basicConfig()
