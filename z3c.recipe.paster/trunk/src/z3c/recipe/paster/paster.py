##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""PasteScript recipe for setup a paste.script.command.run call for Zope3 apps

$Id:$
"""

import zc.recipe.egg


class PasterSetup(zc.recipe.egg.Scripts):
    """Paster setup script."""

    def __init__(self, buildout, name, options):
        if options.get('eggs') is None:
            raise zc.buildout.UserError(
                'You have to define at least one egg for setup a paster.')

        # add PasteScript egg
        options['eggs'] = '%s\nPasteScript' % options.get('eggs')
        super(PasterSetup, self).__init__(buildout, name, options)
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def install(self):
        # install paste.script.command.run
        dest = []
        extra_paths = self.egg.extra_paths
        eggs, ws = self.egg.working_set()
        dest.extend(zc.buildout.easy_install.scripts(
            [('%s'% self.name, 'paste.script.command', 'run')],
            ws, self.options['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            interpreter=self.options.get('interpreter'),
            initialization=self.options.get('initialization', ''),
            arguments=self.options.get('arguments', ''),
            ))

        return dest
