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
import sets
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
    """Application state and logic for **zpkg**."""

    def __init__(self, options):
        """Initialize the application based on an options object as
        returned by `parse_args()`.
        """
        self.logger = logging.getLogger(options.program)
        self.ip = None
        self.options = options
        self.resource = locationmap.normalizeResourceId(options.resource)
        self.resource_type, self.resource_name = self.resource.split(":", 1)
        # Create a new directory for all temporary files to go in:
        self.tmpdir = tempfile.mkdtemp(prefix=options.program + "-")
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

        if self.resource not in self.locations:
            self.error("unknown resource: %s" % self.resource)
        self.resource_url = self.locations[self.resource]
        self.handled_resources = sets.Set()

    def error(self, message, rc=1):
        print >>sys.stderr, message
        sys.exit(rc)

    def build_distribution(self):
        """Create the distribution tree.

        This method performs common actions for both types of
        distribution, and then dispatches to either
        `build_collection_distribution()` or
        `build_package_distribution()` based on the type of the
        primary resource.
        """
        # This could be either a package distribution or a collection
        # distribution; it's the former if there's an __init__.py in
        # the source directory.
        os.mkdir(self.destination)
        self.ip = include.InclusionProcessor(self.source, loader=self.loader)
        self.ip.add_manifest(self.destination)
        self.handled_resources.add(self.resource)
        name = "build_%s_distribution" % self.resource_type
        method = getattr(self, name)
        method()

    def build_package_distribution(self):
        pkgname = self.metadata.name
        pkgdest = os.path.join(self.destination, pkgname)
        try:
            self.ip.createDistributionTree(pkgdest)
        except cvsloader.CvsLoadingError, e:
            self.error(str(e))
        pkgdir = os.path.join(self.destination, pkgname)
        pkginfo = package.loadPackageInfo(pkgname, pkgdir, pkgname)
        self.generate_setup_cfg(self.destination, pkginfo)
        self.generate_package_setup(self.destination, self.resource_name)
        deps_path = os.path.join(self.source, "DEPENDENCIES.cfg")
        if os.path.isfile(deps_path):
            shutil.copy(deps_path,
                        os.path.join(self.destination, "DEPENDENCIES.cfg"))

    def build_application_distribution(self):
        packages, collections = self.assemble_collection()
        # need to generate the configure script and Makefile.in
        metavars = {
            "PACKAGE_FULL_NAME": self.metadata.name,
            "PACKAGE_SHORT_NAME": self.resource_name,
            "PACKAGE_VERSION": self.options.version,
            }
        appsupport = os.path.join(zpkgtools.__path__[0], "appsupport")
        self.copy_template(appsupport, "configure", metavars)
        self.copy_template(appsupport, "Makefile.in", metavars)
        self.copy_template(appsupport, "README.txt", metavars)
        self.generate_collection_setup(self.destination, self.resource_name,
                                       packages, collections,
                                       filename="install.py")

    def copy_template(self, sourcedir, name, metavars):
        template = os.path.join(sourcedir, name) + ".in"
        output = os.path.join(self.destination, name)
        self.ip.add_output(output)
        f = open(template)
        text = f.read()
        f.close()
        for var in metavars:
            text = text.replace("@%s@" % var, metavars[var])
        f = open(output, "w")
        f.write(text)
        f.close()
        shutil.copymode(template, output)

    def build_collection_distribution(self):
        packages, collections = self.assemble_collection()
        self.generate_collection_setup(self.destination, self.resource_name,
                                       packages, collections)

    def assemble_collection(self):
        # Build the destination directory:
        deps = self.add_component("collection",
                                  self.resource_name,
                                  self.source)
        remaining = deps - self.handled_resources
        collections = []
        packages = []
        unhandled_resources = sets.Set()
        while remaining:
            resource = remaining.pop()
            type, name = resource.split(":", 1)
            #
            if resource not in self.locations:
                # it's an external dependency, so we do nothing for now
                self.logger.warn("ignoring resource %r (no source)"
                                 % resource)
                unhandled_resources.add(resource)
                # but we only want to warn about it once, so say we handled it
                self.handled_resources.add(resource)
                continue
            #
            if type == "package":
                packages.append(name)
            elif type == "collection":
                collections.append(name)
            else:
                # must be an external dependency, 'cause we don't know about it
                unhandled_resources.add(resource)
                continue
            #
            source = self.loader.load(self.locations[resource])
            self.handled_resources.add(resource)
            deps = self.add_component(type, name, source)
            if type == "package" and "." in name:
                # this is a sub-package; always depend on the parent package
                i = name.rfind(".")
                deps.add("package:" + name[:i])
            remaining |= (deps - self.handled_resources)
        if unhandled_resources:
            deps_path = os.path.join(self.destination, "DEPENDENCIES.cfg")
            deps = list(unhandled_resources)
            deps.sort()
            f = open(deps_path, "w")
            for dep in deps:
                type, name = dep.split(":", 1)
                if type == "package":
                    dep = name
                print >>f, dep
            f.close()
        return packages, collections

    def add_component(self, type, name, source):
        """Add a single component to a collection.

        :return: Set of dependencies for the added component.
        :rtype: sets.Set

        :param type:
          The type of the resource from the resource identifier.

        :param name:
          The name of the resource from the resource identifier.  This
          is used as the directory name for the component within the
          collection distribution.

        :param source:
          Directory containing the source of the component.

        """
        destination = os.path.join(self.destination, name)
        self.ip.add_manifest(destination)
        spec = include.Specification(source)
        include_path = os.path.join(source, "INCLUDE.cfg")
        if os.path.isfile(include_path):
            f = open(include_path)
            try:
                spec.load(f, include_path)
            finally:
                f.close()

        if type == "package":
            self.add_package_component(name, destination, spec)
        elif type == "collection":
            self.add_collection_component(name, destination, spec)

        self.create_manifest(destination)
        deps_file = os.path.join(source, "DEPENDENCIES.cfg")
        if os.path.isfile(deps_file):
            f = open(deps_file)
            try:
                return dependencies.load(f)
            finally:
                f.close()
        else:
            return sets.Set()

    def add_collection_component(self, name, destination, spec):
        try:
            self.ip.createDistributionTree(destination, spec)
        except cvsloader.CvsLoadingError, e:
            self.error(str(e))
        # load package information and generate setup.cfg
        pkginfo = package.loadCollectionInfo(destination)
        self.generate_setup_cfg(destination, pkginfo)

    def add_package_component(self, name, destination, spec):
        os.mkdir(destination)
        pkgdest = os.path.join(destination, name)
        try:
            self.ip.createDistributionTree(pkgdest, spec)
        except cvsloader.CvsLoadingError, e:
            self.error(str(e))
        # load package information and generate setup.cfg
        pkginfo = package.loadPackageInfo(name, pkgdest, name)
        self.generate_setup_cfg(destination, pkginfo)
        self.generate_package_setup(destination, name)

    def load_metadata(self):
        metadata_file = os.path.join(self.source, "PUBLICATION.cfg")
        if not os.path.isfile(metadata_file):
            self.error("source-dir does not contain required"
                       " publication data file")
        f = open(metadata_file)
        try:
            self.metadata = publication.load(f)
        finally:
            f.close()
        if self.resource_type == "collection":
            # If this is an application collection, change the
            # resource_type to "application":
            from email.Parser import Parser
            parser = Parser()
            f = open(metadata_file)
            msg = parser.parse(f, headersonly=True)
            apptypes = msg.get_all("Installation-type", [])
            if len(apptypes) > 1:
                self.error("installation-type can only be"
                           " specified once in PUBLICATION.cfg")
            if apptypes and apptypes[0].lower() == "application":
                # This is an application rather than a normal collection
                self.resource_type = "application"

    def load_resource(self):
        """Load the primary resource and initialize internal metadata."""
        self.source = self.loader.load(self.resource_url)
        self.load_metadata()
        if not self.options.release_name:
            self.options.release_name = self.metadata.name.replace(" ", "-")
        release_name = self.options.release_name
        self.target_name = "%s-%s" % (release_name, self.options.version)
        self.target_file = self.target_name + ".tar.bz2"
        self.destination = os.path.join(self.tmpdir, self.target_name)

    def generate_package_setup(self, destination, name):
        """Generate the setup.py file for a package distribution.

        :Parameters:
          - `destination`: Directory to write the setup.py into.
          - `name`: Name of the collection.

        """
        setup_py = os.path.join(destination, "setup.py")
        self.ip.add_output(setup_py)
        f = open(setup_py, "w")
        print >>f, SETUP_HEADER
        print >>f, "context = zpkgtools.setup.PackageContext("
        print >>f, "    %r, %r, __file__)" % (name, self.options.version)
        print >>f
        print >>f, "context.setup()"
        f.close()

    def generate_collection_setup(self, destination, name,
                                  packages, collections, filename="setup.py"):
        """Generate the setup.py file for a collection distribution.

        :Parameters:
          - `destination`: Directory to write the setup.py into.
          - `name`: Name of the collection.
          - `packages`: List of packages that are included.
          - `collections`: List of collections that are included.

        Each of these components must be present in a child directory
        of ``self.destination``; the directory name should match the
        component name in these lists.
        """
        setup_py = os.path.join(destination, filename)
        self.ip.add_output(setup_py)
        f = open(setup_py, "w")
        print >>f, SETUP_HEADER
        print >>f, "context = zpkgtools.setup.CollectionContext("
        print >>f, "    %r, %r, __file__," % (name, self.options.version)
        if collections:
            f.write("    collections=[%r" % collections[0])
            for n in collections[1:]:
                f.write(",\n                 %r" % n)
            f.write("],\n")
        if packages:
            f.write("    packages=[%r" % packages[0])
            for n in packages[1:]:
                f.write(",\n              %r" % n)
            f.write("],\n")
        print >>f, "    )"
        print >>f
        print >>f, "context.setup()"
        f.close()

    def generate_setup_cfg(self, destination, pkginfo):
        """Write a setup.cfg file for a distribution component.

        :Parameters:
          - `destination`: Directory the setup.cfg file should be
            written to.
          - `pkginfo`: Package information loaded from a package's
            INSTALL.cfg file.

        The generated setup.cfg will contain some settings applied for
        all packages, and the list of documentation files from the
        component.
        """
        setup_cfg = os.path.join(destination, "setup.cfg")
        self.ip.add_output(setup_cfg)
        f = open(setup_cfg, "w")
        if pkginfo.documentation:
            prefix = "doc_files = "
            s = "\n" + (" " * len(prefix))
            f.write("[bdist_rpm]\n")
            f.write(prefix)
            f.write(s.join(pkginfo.documentation))
            f.write("\n\n")
        f.write("[install_lib]\n")
        # generate .pyc files
        f.write("compile = 1\n")
        # generate .pyo files using "python -O"
        f.write("optimize = 1\n")
        f.close()

    def include_support_code(self):
        """Include any support code needed by the generated setup.py
        files.

        This will add the ``setuptools`` and ``zpkgtools`` packages to
        the output directory if not already present, but they won't be
        added to the set of packages that will be installed by the
        resulting distribution.
        """
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
        """Add the support package `name` to the output directory.

        :Parameters:
          - `name`:  The name of the package to include.

          - `fallback`: Location to use if the package isn't found
            anywhere else.  This will typically be a cvs: URL.

        If a directory named `name` is already present in the output
        tree, it is left unchanged.
        """
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

    def create_manifest(self, destination):
        """Write out a MANIFEST file for the directory `destination`.

        :param destination:
          Directory in the output tree for which a manifest is
          needed.

        Once this has been called for a directory, no further files
        should be written to the directory tree rooted at
        `destination`.
        """
        manifest_path = os.path.join(destination, "MANIFEST")
        self.ip.add_output(manifest_path)
        manifest = self.ip.drop_manifest(destination)
        # XXX should check whether MANIFEST exists already; how to handle?
        f = file(manifest_path, "w")
        for name in manifest:
            print >>f, name
        f.close()

    def create_tarball(self):
        """Generate a compressed tarball from the destination tree.

        The completed tarball is copied to the current directory.
        """
        pwd = os.getcwd()
        os.chdir(self.tmpdir)
        try:
            rc = os.spawnlp(os.P_WAIT, "tar",
                            "tar", "cjf", self.target_file, self.target_name)
        finally:
            os.chdir(pwd)
        if rc:
            self.error("error generating %s" % self.target_file)
        # We have a tarball; clear some space, then copy the tarball
        # to the current directory:
        shutil.rmtree(self.destination)
        shutil.copy(os.path.join(self.tmpdir, self.target_file),
                    self.target_file)

    def cleanup(self):
        """Remove all temporary data storage."""
        shutil.rmtree(self.tmpdir)

    def run(self):
        """Run the application, using the other methods of the
        ``Application`` object.
        """
        try:
            try:
                self.load_resource()
                self.build_distribution()
                if self.options.include_support_code:
                    self.include_support_code()
            except cvsloader.CvsLoadingError, e:
                self.error(str(e), e.exitcode)
            self.create_manifest(self.destination)
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


def parse_args(argv):
    """Parse the command line, return an options object and the
    identifier of the resource to be packaged.

    :return: Options object containing values derived from the command
      line, the name of the application, and the name of the resource
      to operate on.

    :param argv: The command line arguments, including argv[0].

    """

    prog=os.path.basename(argv[0])
    parser = optparse.OptionParser(
        prog=prog,
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
    options, args = parser.parse_args(argv[1:])
    if len(args) != 1:
        parser.error("wrong number of arguments")
    options.program = prog
    options.args = args
    options.resource = args[0]
    return options


def main(argv=None):
    """Main function for **zpkg**.

    :return: Result code for the process.

    :param argv: Command line that should be used.  If omitted or
      ``None``, ``sys.argv`` will be used instead.

    """
    if argv is None:
        argv = sys.argv
    try:
        options = parse_args(argv)
    except SystemExit, e:
        print >>sys.stderr, e
        return 2

    try:
        app = Application(options)
        app.run()
    except SystemExit, e:
        return e.code
    except KeyboardInterrupt:
        return 1
    else:
        return 0
