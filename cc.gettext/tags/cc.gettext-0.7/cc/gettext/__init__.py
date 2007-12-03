##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Compile gettext catalogs from .po files.
"""

import os
import logging
import zc.buildout
from pythongettext.msgfmt import Msgfmt

class MsgFmtRecipe:

    def __init__(self, buildout, name, options):

        self.name, self.buildout, self.options = buildout, name, options
        
        # perform sanity checking on parameters
        if 'po_path' not in options:
            # no po_path provided; use our default
            options['po_path'] = os.path.join(
                buildout['buildout']['directory'], 'i18n')
            logging.getLogger(name).info(
                "No source path for .po files specified; using %s",
                options['po_path'])
        else:
            # make sure the path is absolute
            options['po_path'] = os.path.abspath(options['po_path'])

        if 'mo_path' not in options:
            # no mo_path provided; use our default
            options['mo_path'] = os.path.join(
                buildout['buildout']['directory'], 'locales')
            logging.getLogger(name).info(
                "No target path for .mo files specified; using %s",
                options['mo_path'])
        else:
            # make sure the path is absolute
            options['mo_path'] = os.path.abspath(options['mo_path'])


        # make sure mo_path and po_path exist
        if not(os.path.exists(options['po_path'])):
            logging.getLogger(name).error(
                "Specified po_path %s does not exist.",
                options['po_path'])

            raise zc.buildout.UserError("Invalid path.")

        if not(os.path.exists(options['mo_path'])):
            logging.getLogger(name).warn(
                "Specified mo_path %s does not exist; attempting to create.",
                options['mo_path'])
            os.makedirs(options['mo_path'])

    def install(self):
        """Scan the po_path for .po files and compile them using msgfmt."""

        paths = []
        
        for dirpath, dirnames, filenames in os.walk(self.options['po_path']):

            for po_fn in filenames:
                if po_fn[-3:] != '.po': continue

                # construct the .mo filename
                mo_fn = os.path.join(self.options['mo_path'], 
                                     dirpath[len(self.options['po_path'])+1:],
                                     'LC_MESSAGES', 
                                     po_fn.replace('.po', '.mo'))

                if not(os.path.exists(os.path.dirname(mo_fn))):
                    os.makedirs(os.path.dirname(mo_fn))
                
                # run msgfmt for each .po file
                file(mo_fn, 'wb').write(
                    Msgfmt(os.path.join(dirpath, po_fn)).get())
                paths.append(mo_fn)
                
        return paths

    # XXX: Update should really check timestamps or something smart like that
    update = install

    
