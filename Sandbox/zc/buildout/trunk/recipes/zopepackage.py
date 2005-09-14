##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
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

import buildout

class Default:

    def get(self):
        pass

    def build(self):
        pass

    def install(self):
        if not os.path.exists('instance/lib/python/zope'):
            os.mkdir('instance/lib/python/zope')

        if not os.path.exists('instance/lib/python/zope/__init__.py'):
            f = open('instance/lib/python/zope/__init__.py', 'w')
            f.write(
                "from pkgutil import extend_path\n"
                "__path__ = extend_path(__path__, __name__)\n"
                )
            f.close()

    def freshen(self):
        pass
