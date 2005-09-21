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
#!/usr/bin/env python

import pickle, shutil, sys, re, warnings

from util import *
import util

MIRRORED_SUBVERSION_COMMANDS = ['up', 'update', 'stat', 'status', 'revert',
                                'diff', 'commit']

def getRecipe(module):
    if sys.platform == 'win32' and hasattr(module, 'Windows'):
        recipe = module.Windows()
    else:
        recipe = module.Default()
    return recipe

def get(modules, packages):
    try:
        version_file = open('.version_info', 'rb')
    except IOError:
        old_packages = {}
    else:
        old_packages = pickle.load(version_file)
        version_file.close()

    new_packages = {}
    for module, (package, version) in zip(modules, packages):
        activityDot()
        if isExternal(package):
            old_version = old_packages.get(package)
            if old_packages and old_version and old_version != version:
                warnings.warn('You changed an external package\'s version.')
            if util.verbose:
                print 'buildout: skipping external', package
            continue

        # record the version info for non-external packages
        new_packages[package] = version

        source_path = getSourcePath(package)
        build_path = getBuildPath(package)
        if old_packages and old_packages.get(package) != version \
        and (os.path.exists(source_path) or os.path.exists(build_path)):
            answer = raw_input('About to delete "%s" and get a new version, '
                               'ok? [yes|no] ' % package)
            if answer != 'yes':
                raise SystemExit
            util.rmtree(source_path)
            util.rmtree(build_path)

        chdir('.')

        if util.verbose:
            print 'buildout: getting', package

        recipe = getRecipe(module)
        recipe.get()
        popdir()

    # keep package version information so we know when they change
    saved_packages = {}
    saved_packages.update(old_packages)
    saved_packages.update(new_packages)
    version_file = open('.version_info', 'wb')
    pickle.dump(saved_packages, version_file, -1)
    version_file.close()

def build(modules, packages):
    for module, (package, version) in zip(modules, packages):
        activityDot()
        if isExternal(package):
            if util.verbose:
                print 'buildout: skipping external', package
            continue

        chdir('.')

        if util.verbose:
            print 'buildout: building', package

        recipe = getRecipe(module)
        recipe.build()
        popdir()

def install(modules, packages):
    for module, (package, version) in zip(modules, packages):
        activityDot()
        chdir('.')
        if util.verbose:
            print 'buildout: installing', package

        recipe = getRecipe(module)
        recipe.install()
        popdir()

def freshen(modules, packages):
    for module, (package, version) in zip(modules, packages):
        activityDot()
        if isExternal(package):
            if util.verbose:
                print 'buildout: skipping external', package
            continue
        chdir('.')
        if util.verbose:
            print 'buildout: freshening', package

        recipe = getRecipe(module)
        recipe.freshen()
        popdir()

def subversionCommand(command, packages):
    paths = [getSourcePath(package) for package, version in packages]
    paths.append(getBasePath())
    for source_path in paths:
        try:
            prefix = os.path.commonprefix([getBasePath(), source_path])
            path = source_path[len(prefix)+1:]
            options = []
            if command not in ['revert', 'status', 'diff', 'commit']:
                options.append('--quiet')
            if command == 'revert':
                options.append('--recursive')
            else:
                options.append('--non-interactive')
            child_in, child_out = os.popen4('svn %s %s ' 
                                            % (command, ' '.join(options))
                                            + path)

            child_in.close()
            output = child_out.read()
            child_out.close()

            # we want to ignore messages about non-revision-controled packages
            if 'is not a working copy' in output:
                continue
            else:
                # clean up the subversion output a bit
                for pattern in [r'Performing status on external item at .*', 
                                r'X.*\n', r'\n(?=\n)']:
                    output = re.sub(pattern, '', output)
                if output.strip():
                    sys.stdout.write(output)
        except OSError, e:
            if e.errno != errno.ENOENT: # no such file or directory
                raise
            
def main(argv):
    # really need to use optparse instead
    for index, arg in list(enumerate(argv))[::-1]:
        if arg[:2] == '-v':
            arg = arg[1:]
            while arg[:1] == 'v':
                util.verbose += 1
                arg = arg[1:]
            del argv[index]

    if util.verbose == 0:
        print 'working...',
        sys.stdout.flush()

    # get the packages to be built, and their respective versions
    packages = getPackages()

    # build up a list of modules
    modules = [__import__('recipes.'+p, {}, {}, 'recipes')
               for p,v in packages]
    if len(argv) == 1: # If no arguments, freshen and then build.
        get(modules, packages)
        freshen(modules, packages)
        build(modules, packages)
        install(modules, packages)
        setUpPackages()
    elif len(argv) == 2 and argv[1] == 'get':
        get(modules, packages)
    elif len(argv) == 2 and argv[1] in MIRRORED_SUBVERSION_COMMANDS:
        subversionCommand(argv[1], packages)
    elif len(argv) == 2 and argv[1] == 'freshen':
        freshen(modules, packages)
    elif len(argv) == 2 and argv[1] == 'ini':
        getConfiguration()
    elif len(argv) == 2 and argv[1] == 'build':
        build(modules, packages)
        install(modules, packages)
        setUpPackages()
    elif len(argv) == 2 and argv[1] == 'clobber':
        for p in ['var/src', 'var/opt', 'bin', 'instance']:
            activityDot()
            if os.path.exists(p):
                util.rmtree(p)
    print 'done'
