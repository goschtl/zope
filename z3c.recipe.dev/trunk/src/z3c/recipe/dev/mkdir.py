##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Z3c development recipes

$Id:$
"""

import os
import logging
import zc.buildout


class MkdirSetup:

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.originalPath = options['path']
        options['path'] = os.path.join(buildout['buildout']['directory'],
            self.originalPath)
        self.createPath = options.get('createpath', 'False').lower() in [
            'true', 'on', '1']
        if (    not self.createPath
            and not os.path.isdir(os.path.dirname(options['path']))
           ):
            logging.getLogger(self.name).error(
                'Cannot create %s. %s is not a directory.',
                options['path'], os.path.dirname(options['path']))
            raise zc.buildout.UserError('Invalid Path')

    def install(self):
        path = self.options['path']
        if not os.path.isdir(path):
            logging.getLogger(self.name).info(
                'Creating directory %s', self.originalPath)
            os.makedirs(path)
        return ()

    def update(self):
        pass

