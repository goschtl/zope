##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Create a system deployment for an application

$Id: deployment.py 14934 2006-11-10 23:57:33Z jim $
"""

import os, pwd, shutil

class Recipe:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        options['run-directory'] = os.path.join(options.get('run', '/var/run'),
                                                name)
        options['log-directory'] = os.path.join(options.get('log', '/var/log'),
                                                name)
        options['etc-directory'] = os.path.join(options.get('etc', '/etc'),
                                                name)

    def install(self):
        options = self.options
        user = options['user']
        uid, gid = pwd.getpwnam(user)[2:4]
        created = []
        try:
            for d in 'run', 'log', 'etc':
                d = options[d+'-directory']
                if not os.path.isdir(d):
                    os.mkdir(d, 0775)
                    os.chmod(d, 0775)
                    os.chown(d, uid, gid)
                    created.append(d)
            return created
        except:
            for d in created:
                shutil.rmtree(d)
            raise

    def update(self):
        pass
