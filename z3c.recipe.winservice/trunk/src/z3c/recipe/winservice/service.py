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
import string
import shutil
import zc.buildout


def installScript(srcFile, script, replacements):
    generated = []

    # generate the winservice script
    text = open(srcFile, "rU").read()
    # perform replacements
    for var, string in replacements:
        text = text.replace(var, string)

    changed = not (os.path.exists(script) and open(script).read() == text)

    if changed:
        # If the file exists, keep the old file.  This is a
        # hopefully temporary hack to get around distutils
        # stripping the permissions on the server skeleton files.
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

def patchScript(srcFile, dstFile):
    generated = []

    src = open(srcFile, 'rU').read()

    src = '\n'.join(['    '+line for line in src.split('\n')])

    dest = PATCH_TEMPLATE % dict(script=src,
                                 srcFile=srcFile)

    changed = not (os.path.exists(dstFile) and open(dstFile).read() == dest)

    if changed:
        open(dstFile, 'w').write(dest)
        shutil.copymode(srcFile, dstFile)
        shutil.copystat(srcFile, dstFile)

    generated.append(dstFile)

    return generated


PATCH_TEMPLATE = '''
def exceptionlogger():
    import servicemanager
    import traceback
    servicemanager.LogErrorMsg("Script %%s had an exception: %%s" %% (
      __file__, traceback.format_exc()
    ))

try:
%(script)s
except Exception, e:
    exceptionlogger()
'''

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
        options['serviceName'] = self.getServiceName()

    def getServiceName(self):
        try:
            serviceName = self.options['serviceName']
        except KeyError:
            if len(self.runScript) < 128:
                #make a meaningful name in case it fits
                serviceName = ''
                for c in self.runScript:
                    if c in string.letters + string.digits:
                        serviceName += c
                    else:
                        serviceName += '_'
            else:
                #otherwise a dumb hash
                serviceName = str(hash(self.runScript))
        return serviceName

    def install(self):
        options = self.options

        # setup service name
        defaultName = 'Zope3 %s' % self.name
        defaultDescription = 'Zope3 windows service for %s, using %s' % (
            self.name, self.runScript)
        displayName = options.get('name', defaultName)
        serviceName = options['serviceName']
        description = options.get('description', defaultDescription)

        generated = []

        if options.get('debug'):
            serviceScript = self.runScript.replace(
                '-script.py', '-servicedebug.py')
            generated += patchScript(self.runScript, serviceScript)
        else:
            serviceScript = self.runScript

        self.winServiceVars = [
            ("<<PYTHON>>", self.executable),
            ("<<RUNZOPE>>", serviceScript),
            ("<<SERVICE_NAME>>", serviceName),
            ("<<SERVICE_DISPLAY_NAME>>", displayName),
            ("<<SERVICE_DESCRIPTION>>", description),
            ]

        # raise exeption if the app script is not here now
        if not os.path.exists(serviceScript):
            raise zc.buildout.UserError(
                'App start script %s does not exist in bin folder.'  %
                    self.runScript)

        # get templates
        winServiceTemplate = os.path.join(os.path.dirname(__file__),
            'winservice.in')

        # setup winservice file paths
        binDir = self.buildout['buildout']['bin-directory']
        script = os.path.join(binDir, 'winservice.py')

        generated += installScript(winServiceTemplate, script,
            self.winServiceVars)

        # return list of generated files
        return generated

    update = install