##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Top-level application object for **zpkg**."""

import logging
import optparse
import os
import shutil
import sys
import tempfile

import zpkgtools

from zpkgtools import config
from zpkgtools import cvsloader
from zpkgtools import dependencies
from zpkgtools import include
from zpkgtools import locationmap
from zpkgtools import package
from zpkgtools import publication


class Application:

    def __init__(self, options, resource, program):
        self.logger = logging.getLogger(program)
        self.ip = None
        self.options = options
        self.resource = locationmap.normalizeResourceId(resource)
        self.resource_type, self.resource_name = self.resource.split(":", 1)
        # Create a new directory for all temporary files to go in:
        self.tmpdir = tempfile.mkdtemp(prefix=program + "-")
        tempfile.tempdir = self.tmpdir
        if options.revision_tag:
            self.loader = cvsloader.CvsLoader(tag=options.revision_tag)
        else:
            self.loader = cvsloader.CvsLoader()
        cf = config.Configuration()
        cf.location_maps.extend(options.location_maps)
        path = options.configfile
        if path is None:
            path = config.defaultConfigurationPath()
            if os.path.exists(path):
                cf.loadPath(path)
        elif path:
            cf.loadPath(path)

        cf.finalize()
        self.locations = cf.locations
        if options.include_support_code is None:
            options.include_support_code = cf.include_support_code

        if resource not in self.locations:
            print >>sys.stderr, "unknown resource:", resource
            sys.exit(1)
        self.resource_url = self.locations[resource]

    def build_distribution(self):
        # This could be either a package distribution or a collection
        # distribution; it's the former if there's an __init__.py in
        # the source directory.
        os.mkdir(self.destination)
        self.ip = include.InclusionProcessor(self.source)
        name = "build_%s_distribution" % self.resource_type
        method = getattr(self, name)
        method()
        self.generate_setup()

    def build_package_distribution(self):
        pkgname = self.metadata.name

        self.manifest = self.ip.add_manifest(self.destination)
        pkgdest = os.path.join(self.destination, pkgname)
        try:
            self.ip.createDistributionTree(pkgdest)
        except cvsloader.CvsLoadingError, e:
            print >>sys.stderr, e
            sys.exit(1)
        pkgdir = os.path.join(self.destination, pkgname)
        pkginfo = package.loadPackageInfo(pkgname, pkgdir, pkgname)
        if pkginfo.documentation:
            setup_cfg = os.path.join(self.destination, "setup.cfg")
            self.ip.add_output(setup_cfg)
            prefix = "doc_files = "
            s = "\n" + (" " * len(prefix))
            f = open(setup_cfg, "w")
            f.write("[bdist_rpm]\n")
            f.write(prefix)
            f.write(s.join(pkginfo.documentation))
            f.write("\n")
            f.close()

    def build_collection_distribution(self):
        # Build the destination directory:
        self.manifest = self.ip.add_manifest(self.destination)
        try:
            self.ip.createDistributionTree(self.destination)
        except cvsloader.CvsLoadingError, e:
            print >>sys.stderr, e
            sys.exit(1)
        deps_file = os.path.join(self.source, "DEPENDENCIES.txt")
        if os.path.isfile(deps_file):
            for dep in dependencies.load(open(deps_file)):
                if dep in self.locations:
                    # we can get this
                    pass
                else:
                    # external dependency
                    pass

    def load_metadata(self):
        metadata_file = os.path.join(self.source, "PUBLICATION.txt")
        if not os.path.isfile(metadata_file):
            print >>sys.stderr, \
                  "source-dir does not contain required publication data file"
            sys.exit(1)
        self.metadata = publication.load(open(metadata_file))

    def load_resource(self):
        self.source = self.loader.load(self.resource_url)
        self.load_metadata()
        if not self.options.release_name:
            self.options.release_name = self.metadata.name.replace(" ", "-")
        release_name = self.options.release_name
        self.target_name = "%s-%s" % (release_name, self.options.version)
        self.target_file = self.target_name + ".tar.bz2"
        self.destination = os.path.join(self.tmpdir, self.target_name)

    def generate_setup(self):
        setup_py = os.path.join(self.destination, "setup.py")
        self.ip.add_output(setup_py)
        type = self.resource_type
        f = open(setup_py, "w")
        print >>f, SETUP_HEADER
        print >>f, "context = zpkgtools.setup.%sContext(" % type.capitalize()
        print >>f, "    %r, %r, __file__)" % (self.resource_name,
                                              self.options.version)
        print >>f
        print >>f, "context.setup()"
        f.close()

    def include_support_code(self):
        old_loader = self.loader
        if self.options.revision_tag:
            # we really don't want the tagged version of the support code
            self.loader = cvsloader.CvsLoader()
        self.include_support_package(
            "zpkgtools", ("cvs://cvs.zope.org/cvs-repository"
                          ":Packages/zpkgtools/zpkgtools"))
        self.include_support_package(
            "setuptools", ("cvs://cvs.python.sourceforge.net/cvsroot/python"
                           ":python/nondist/sandbox/setuptools/setuptools"))
        if self.options.revision_tag:
            self.loader.cleanup()
        self.loader = old_loader

    def include_support_package(self, name, fallback):
        destination = os.path.join(self.destination, name)
        if os.path.exists(destination):
            # have the package as a side effect of something else
            return
        source = None
        if name in self.locations:
            url = self.locations[name]
        else:
            try:
                __import__(name)
            except ImportError:
                url = fallback
                self.logger.info("resource package:%s not configured;"
                                 " using fallback URL" % name)
            else:
                mod = sys.modules[name]
                source = os.path.abspath(mod.__path__[0])
        if source is None:
            source = self.loader.load(url)

        tests_dir = os.path.join(source, "tests")
        self.ip.copyTree(source, destination, excludes=[tests_dir])

    def create_manifest(self):
        if self.ip is None:
            return
        manifest_path = os.path.join(self.destination, "MANIFEST")
        self.ip.add_output(manifest_path)
        f = file(manifest_path, "w")
        for name in self.manifest:
            print >>f, name
        f.close()

    def create_tarball(self):
        pwd = os.getcwd()
        os.chdir(self.tmpdir)
        try:
            rc = os.spawnlp(os.P_WAIT, "tar",
                            "tar", "cjf", self.target_file, self.target_name)
        finally:
            os.chdir(pwd)
        if rc:
            print >>sys.stderr, "error generating", self.target_file
            sys.exit(1)
        # We have a tarball; clear some space, then copy the tarball
        # to the current directory:
        shutil.rmtree(self.destination)
        shutil.copy(os.path.join(self.tmpdir, self.target_file),
                    self.target_file)

    def cleanup(self):
        shutil.rmtree(self.tmpdir)

    def run(self):
        try:
            try:
                self.load_resource()
                self.build_distribution()
                if self.options.include_support_code:
                    self.include_support_code()
            except cvsloader.CvsLoadingError, e:
                print >>sys.stderr, e
                sys.exit(e.exitcode)
            self.create_manifest()
            self.create_tarball()
            self.cleanup()
        except:
            print >>sys.stderr, "temporary files are in", self.tmpdir
            raise


SETUP_HEADER = """\
#! /usr/bin/env python
#
# THIS IS A GENERATED FILE.  DO NOT EDIT THIS DIRECTLY.

import zpkgtools.setup

"""


def parse_args(args):
    parser = optparse.OptionParser(
        usage="usage: %prog [options] resource",
        version="%prog 0.1")
    parser.add_option(
        "-C", "--configure", dest="configfile",
        help="path or URL to the configuration file", metavar="FILE")
    parser.add_option(
        "-f", dest="configfile",
        action="store_const", const="",
        help="don't read a configuration file")
    parser.add_option(
        "-m", "--resource-map", dest="location_maps",
        action="append", default=[],
        help=("specify an additional location map to load before"
              " maps specified in the configuration"), metavar="MAP")
    parser.add_option(
        "-n", "--name", dest="release_name",
        help="base name of the distribution file", metavar="NAME")
    parser.add_option(
        "-r", "--revision-tag", dest="revision_tag",
        help="default CVS tag to use (default: HEAD)", metavar="TAG",
        default="HEAD")
    parser.add_option(
        "-S", dest="include_support_code", action="store_false",
        help="don't include copies of the zpkgtools support code")
    parser.add_option(
        "-s", dest="include_support_code", action="store_true",
        help="include copies of the zpkgtools support code (the default)")
    parser.add_option(
        "-v", dest="version",
        help="version label for the new distribution",
        default="0.0.0")
    return parser.parse_args(args)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    options, args = parse_args(argv[1:])

    # figure out what to read from:
    if len(args) != 1:
        print >>sys.stderr, "wrong number of arguments"
        return 2
    resource = args[0]
    program = os.path.basename(argv[0])

    try:
        app = Application(options, resource, program)
        app.run()
    except SystemExit, e:
        return e.code
    except KeyboardInterrupt:
        return 1
    else:
        return 0
