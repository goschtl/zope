"""base classes

$Id$
"""
__docformat__ = 'ReStructuredText'
import StringIO
import base64
import httplib
import logging
import optparse
import os
import pkg_resources
import subprocess
import sys
import urllib2
import urlparse

from zope.wineggbuilder import base

LOGGER = base.LOGGER

def getOption(config, section, name, default=None):
    try:
        return config.get(section, name)
    except ConfigParser.NoOptionError:
        self.uploadType = 'internal'


class Compiler(object):
    def __init__(self, name, config, options):
        self.name = name
        self.options = options
        self.read(config)

    def read(self, config):
        self.command = config.get(self.name, 'command')
        self.fileEnding = config.get(self.name, 'fileEnding')

class Package(object):
    def __init__(self, name, config, options, compilers):
        self.name = name
        self.options = options
        self.read(config, compilers)

    def read(self, config):
        self.pypiurl = config.get(self.name, 'pypiurl')
        self.tagurl = config.get(self.name, 'tagurl')
        self.minVersion = getOption(config, self.name, 'minVersion')
        self.maxVersion = getOption(config, self.name, 'maxVersion')
        self.targets = []
        for target in config.get(self.name, 'targets').split():
            self.targets.append(compilers[target])

    def build(self):
        pass
        #1 get versions from pypi
        #2 get file list of the version
        #3 check file endings
        #4 build missing

class Builder(object):
    def __init__(self, configFileName, options):
        config = ConfigParser.RawConfigParser()
        config.read(configFileName)

        self.compilers = {}
        for cmp in config.get(base.BUILD_SECTION, 'compilers').split():
            self.compilers[cmp] = Compiler(cmp, config, options)

        self.packages = []
        for pkg in config.get(base.BUILD_SECTION, 'packages').split():
            self.packages.append(Package(pkg, config, options, self.compilers))

        for pkg in self.packages:
            pkg.build()


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

    logger.setLevel(logging.INFO)
    if options.verbose:
        logger.setLevel(logging.DEBUG)
    if options.quiet:
        logger.setLevel(logging.FATAL)

    if len(args) == 0:
        print "No configuration was specified."
        print "Usage: %s [options] config1 config2 ..." % sys.argv[0]
        sys.exit(0)

    for configFileName in args:
        builder = Builder(configFileName, options)

        try:
            builder.runCLI()
        except KeyboardInterrupt:
            logger.info("Quitting")
            sys.exit(0)

    # Remove the handler again.
    logger.removeHandler(handler)

    # Exit cleanly.
    sys.exit(0)
