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
"""Main builder stuff
"""
__docformat__ = 'ReStructuredText'
import StringIO
import base64
import httplib
import logging
import optparse
import os
import pkg_resources
import re
import subprocess
import sys
import tempfile
import urllib2
import urlparse
from collections import defaultdict

import BeautifulSoup
import ConfigParser
from distutils.version import StrictVersion

from zope.wineggbuilder import base

LOGGER = base.LOGGER

def getOption(config, section, name, default=None):
    try:
        return config.get(section, name)
    except ConfigParser.NoOptionError:
        return default


class Compiler(object):
    #hook to enable testing
    commandKlass = base.Command

    def __init__(self, name, config, options):
        self.name = name
        self.options = options
        self.read(config)

    def read(self, config):
        self.command = config.get(self.name, 'command')
        self.fileEnding = config.get(self.name, 'fileEnding')

    def checkBuild(self, package, version, files):
        """check whether build is required"""
        LOGGER.debug('Checking if build required for [%s] %s %s %s',
                     package.sectionName, package.name, version, self.name)
        needBuild = True
        fe = self.fileEnding.lower()
        for file in files:
            if file.lower().endswith(fe):
                needBuild = False
                break

        if needBuild:
            LOGGER.debug('Build required for [%s] %s %s %s',
                     package.sectionName, package.name, version, self.name)
        else:
            LOGGER.debug('Build not required for [%s] %s %s %s',
                     package.sectionName, package.name, version, self.name)
        return needBuild

    def build(self, package, version, files, sourceFolder, status):
        LOGGER.info('Starting build for [%s] %s %s %s',
                    package.sectionName, package.name, version, self.name)
        #we really need to build
        #we have the source in sourceFolder
        cmd = self.commandKlass(cwd=sourceFolder, exitOnError=False)
        command = self.command

        if self.options.dryrun:
            LOGGER.info("Dry run, no upload")
            command = command.replace('upload', '')
            status.setStatus(package, version, "dryrun", self)

        LOGGER.debug('Running: %s\nIn: %s', command, sourceFolder)

        tmpfile = None
        if len(command.splitlines()) > 1:
            #in case there are more lines we got to do .bat file
            tmpfile = tempfile.mktemp(suffix='.bat')
            open(tmpfile, "w").write(command)
            command = tmpfile

        try:
            #this ought to build and upload the egg
            output = cmd.do(command)
            if 'failed' in output.lower():
                LOGGER.info("Something was wrong with the command. Output: %s",
                            output)
                status.setStatus(package, version, "failed", self)

            if 'running upload' in output \
                and 'Submitting' in output \
                and 'Server response (200): OK' in output:
                LOGGER.info("Upload seems to be OK.\n%s",
                            '\n'.join(output.splitlines()[-3:]))
                status.setStatus(package, version, "done", self)
        except KeyboardInterrupt:
            raise
        except:
            #prepare for the worst
            LOGGER.exception("An error occurred while running the build command")
            #continue without bailing out
            status.setStatus(package, version, "error", self)

        if tmpfile:
            os.remove(tmpfile)

class Package(object):
    #hook to enable testing
    pypiKlass = base.PYPI
    urlGetterKlass = base.URLGetter
    svnKlass = base.SVN

    def __init__(self, sectionName, config, options, compilers):
        self.sectionName = sectionName
        self.options = options
        self.read(sectionName, config, compilers)

    def read(self, sectionName, config, compilers):
        self.name = config.get(sectionName, 'package')
        self.pypiurl = getOption(config, sectionName, 'pypiurl',
                                 'http://pypi.python.org/simple/%s/' % self.name)
        self.tagurl = getOption(config, sectionName, 'tagurl',
                                'svn://svn.zope.org/repos/main/%s/tags' % self.name)
        if self.tagurl.endswith('/'):
            self.tagurl = self.tagurl[:-1]
        self.minVersion = getOption(config, sectionName, 'minVersion')
        self.maxVersion = getOption(config, sectionName, 'maxVersion')
        self.needSource = bool(getOption(config, sectionName, 'needSource', 'True'))
        self.excludeVersions = getOption(
            config, sectionName, 'excludeVersions' ,'').split()
        self.targets = []
        for target in config.get(sectionName, 'targets').split():
            self.targets.append(compilers[target])

    def build(self, status):
        LOGGER.info("Processing %s [%s]", self.name, self.sectionName)

        #1 get versions from pypi
        pypi = self.pypiKlass()
        versions = pypi.package_releases(self.name, show_hidden=True)

        status.setVersions(self, versions)

        #1.1 filter versions according to minVersion and maxVersion:
        if self.minVersion:
            minver = StrictVersion(self.minVersion)
            ov = []
            for v in versions:
                try:
                    if StrictVersion(v) >= minver:
                        ov.append(v)
                except ValueError:
                    pass
            versions = ov

        if self.maxVersion:
            maxver = StrictVersion(self.maxVersion)
            ov = []
            for v in versions:
                try:
                    if StrictVersion(v) <= maxver:
                        ov.append(v)
                except ValueError:
                    pass
            versions = ov

        versions = [v for v in versions
                    if v not in self.excludeVersions]

        versions.sort()
        if len(versions) == 0:
            #nothing to do
            LOGGER.info('%s no versions, nothing to do', self.name)
            return

        #2 get file list of each version
        LOGGER.debug('getting %s', self.pypiurl)

        verFiles = defaultdict(list)
        simple = self.urlGetterKlass().get(self.pypiurl)
        soup = BeautifulSoup.BeautifulSoup(simple)
        VERSION = re.compile(self.name+r'-(\d+\.\d+(\.\d+\w+){0,2})')
        gotSource = False

        for tag in soup('a'):
            cntnt = str(tag.contents[0]) # str: re does not like non-strings

            if self.sectionName == 'ZODB3_2664' and '3.10' in cntnt:
                from pub.dbgpclient import brk; brk('192.168.32.1')

            m = VERSION.search(cntnt)
            if m:
                version = m.group(1)
                if version not in versions:
                    continue
                LOGGER.debug('Got a file: %s', cntnt)
                verFiles[version].append(cntnt)

                if (cntnt.endswith('.zip')
                    or cntnt.endswith('.tar.gz')
                    or cntnt.endswith('tgz')):
                    gotSource = True

        if self.needSource and not gotSource:
            LOGGER.info("No source release (.zip/.tar.gz/.tgz) found")

        svn = self.svnKlass(exitOnError=False)
        for version in versions:
            #3 check whether we need a build
            needs = []
            for target in self.targets:
                needBuild = target.checkBuild(
                    self, version, verFiles.get(version, []))
                if needBuild:
                    needs.append(target)
                else:
                    status.setStatus(self, version, "existed", target)

            if needs:
                tmpfolder = tempfile.mkdtemp('wineggbuilder')
                try:
                    try:
                        #3.1 svn co tag
                        svnurl = "%s/%s" % (self.tagurl, version)
                        svn.co(svnurl, tmpfolder)
                    except OSError:
                        status.setStatus(self, version, "SVN error")
                    else:
                        #3.2 build missing
                        for target in needs:
                            needBuild = target.build(
                                self, version, verFiles.get(version, []),
                                tmpfolder, status)
                finally:
                    #3.3 del temp folder
                    base.rmtree(tmpfolder)

class Status(object):
    def __init__(self, packages, targets):
        self.data = {}
        self.packages = packages
        self.targets = targets

        for p in packages:
            self.data[p.name] = {}

    def setVersions(self, package, versions):
        for v in versions:
            self.data[package.name].setdefault(v, {})
            for t in self.targets:
                self.data[package.name][v].setdefault(t, 'n/a')

    def setStatus(self, package, version, status, target=None):
        if target is None:
            # this is a version general status
            for t in self.targets:
                self.data[package.name][version][t] = status
        else:
            self.data[package.name][version][target.name] = status

    def log(self):
        text = ['\n']
        targets = sorted(self.targets.keys())
        vs = ' '.join(['='*10 for target in targets])
        sep = "%s %s" % ('='*20, vs)

        for pname in sorted(self.data.keys()):
            package = self.data[pname]
            vs = ' '.join([target.ljust(10) for target in targets])
            txt = "%s %s" % (pname.ljust(20), vs)
            text.append(sep)
            text.append(txt)
            text.append(sep)
            for vname in sorted(package.keys()):
                version = package[vname]
                if isinstance(version, basestring):
                    txt = "%20s %s" % (vname, version)
                else:
                    vs = ' '.join([version[target].ljust(10)
                                   for target in targets])
                    txt = "%20s %s" % (vname, vs)
                text.append(txt)
        output = '\n'.join(text)
        LOGGER.info(output)


class Builder(object):
    def __init__(self, configFileName, options):
        self.options = options
        LOGGER.info('loading configuration from %s', configFileName)

        config = ConfigParser.RawConfigParser()
        config.read(configFileName)

        self.compilers = {}
        for cmp in config.get(base.BUILD_SECTION, 'compilers').split():
            self.compilers[cmp] = Compiler(cmp, config, options)

        self.packages = []
        for section in sorted(config.sections()):
            if section == base.BUILD_SECTION:
                continue
            if section in self.compilers:
                continue

            self.packages.append(Package(section, config,
                                         options, self.compilers))

    def runCLI(self):
        LOGGER.info('Starting to build')

        status = Status(self.packages, self.compilers)

        for pkg in self.packages:
            try:
                pkg.build(status)
            except KeyboardInterrupt:
                raise
            except:
                #prepare for the worst
                LOGGER.exception("An error occurred while running the building %s",
                                 pkg.name)
                #continue without bailing out

        LOGGER.info('Done.')

        if self.options.status:
            status.log()


def main(args=None):
    # Make sure we get the arguments.
    if args is None:
        args = sys.argv[1:]
    if not args:
        args = ['-h']

    # Set up logger handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(base.formatter)
    LOGGER.addHandler(handler)

    # Parse arguments
    options, args = base.parser.parse_args(args)

    LOGGER.setLevel(logging.INFO)
    if options.verbose:
        LOGGER.setLevel(logging.DEBUG)
    if options.quiet:
        LOGGER.setLevel(logging.FATAL)

    if len(args) == 0:
        print "No configuration was specified."
        print "Usage: %s [options] config1 config2 ..." % sys.argv[0]
        sys.exit(0)

    for configFileName in args:
        builder = Builder(configFileName, options)

        try:
            builder.runCLI()
        except KeyboardInterrupt:
            LOGGER.info("Quitting")
            sys.exit(0)

    # Remove the handler again.
    LOGGER.removeHandler(handler)

    # Exit cleanly.
    #sys.exit(0)
