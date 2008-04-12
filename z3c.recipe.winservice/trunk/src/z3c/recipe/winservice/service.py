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
import shutil
import zc.buildout


def installScript(srcFile, script, replacements):
    generated = []
    
    # generate the winservice script
    text = open(srcFile, "rU").read()
    # perform replacements
    for var, string in replacements:
        text = text.replace(var, string)

    # If the file exists, keep the old file.  This is a
    # hopefully temporary hack to get around distutils
    # stripping the permissions on the server skeletin files.
    # We reuse the original default files, which have the
    # right permissions.
    old = os.path.exists(script)
    if old:
        f = open(script, "r+")
        f.truncate(0)
    else:
        f = open(script, "w")

    f.write(text)
    f.close()

    if not old:
        shutil.copymode(srcFile, script)
        shutil.copystat(srcFile, script)
    generated.append(script)

    return generated


class ServiceSetup:

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        # setup executable
        self.executable = self.buildout['buildout']['executable']

        # setup start script
        binDir = self.buildout['buildout']['bin-directory']
        runzope = options.get('runzope')

        # fix script name
        if not runzope:
            raise zc.buildout.UserError(
                'Missing runzope option in winservice recipe.')
        if not runzope.endswith('-script.py'):
            if runzope.endswith('.py'):
                runzope = runzope[:3]
            runzope = '%s-script.py' % runzope

        self.runScript = os.path.join(binDir, runzope)

        # setup service name
        defaultName = 'Zope3 %s' % self.name
        defaultDescription = 'Zope3 windows service for %s' % self.name
        displayName = options.get('name', defaultName)
        serviceName = str(hash(displayName))
        description = options.get('description', defaultDescription)
        self.winServiceVars = [
            ("<<PYTHON>>", self.executable),
            ("<<RUNZOPE>>", self.runScript),
            ("<<SERVICE_NAME>>", serviceName),
            ("<<SERVICE_DISPLAY_NAME>>", displayName),
            ("<<SERVICE_DESCRIPTION>>", description),
            ]
        self.runZopeVars = []

    def install(self):
        options = self.options
        generated = []

        # raise exeption if the app script is not here now
        if not os.path.exists(self.runScript):
            raise zc.buildout.UserError(
                'App start script %s does not exist in bin folder.'  % 
                    self.runScript)

        # get templates
        binDir = self.buildout['buildout']['bin-directory']
        winServiceTemplate = os.path.join(os.path.dirname(__file__),
            'winservice.in')

        # setup winservice file paths
        script = os.path.join(binDir, 'winservice.py')

        generated += installScript(winServiceTemplate, script,
            self.winServiceVars)

        # return list of generated files
        return generated

    update = install
