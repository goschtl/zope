##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Top-level application object for **zpkg**."""

import optparse
import os
import re
import sets
import shutil
import sys
import tempfile

import ZConfig
import zpkgsetup
import zpkgtools

from zpkgsetup import cfgparser
from zpkgsetup import loggingapi as logging
from zpkgsetup import package
from zpkgsetup import publication
from zpkgsetup import setup
from zpkgsetup import urlutils
from zpkgsetup.utils import rmtree_force

from zpkgtools import config
from zpkgtools import dependencies
from zpkgtools import include
from zpkgtools import loader
from zpkgtools import runlog


def package_resource(package):
    dir = os.path.abspath(package.__path__[0])
    return urlutils.file_url(dir)

DEFAULT_SUPPORT_PACKAGES = [
    ("ZConfig",   package_resource(ZConfig)),
    ("zpkgsetup", package_resource(zpkgsetup)),
    ]


class Application:
    """Application state and logic for **zpkg**."""

    def __init__(self, options):
        """Initialize the application based on an options object as
        returned by `parse_args()`.
        """
        self.logger = logging.getLogger(__name__)
        self.options = options
        cf = config.Configuration()
        # The resource maps and loader tools assume that all resources
        # are being addressed by URLs, so we need to make sure paths
        # referenced on the command line are converted to URLs before
        # loading anything.
        location_maps = []
        for map in options.location_maps:
            if os.path.isfile(map):
                map = urlutils.file_url(os.path.abspath(map))
            location_maps.append(map)
        cf.location_maps.extend(location_maps)
        path = options.configfile
        if path is None:
            path = config.defaultConfigurationPath()
            if not os.path.exists(path):
                path = None
        if path:
            self.logger.debug("loading configuration file %s", path)
            try:
                cf.loadPath(path)
            except cfgparser.ConfigurationError, e:
                self.error(str(e))
        cf.finalize()
        self.locations = cf.locations
        if cf.collect_dependencies:
            self.options.collect = True
        if cf.application:
            self.options.application = True

        self.exclude_packages = sets.Set(cf.exclude_packages)

        # XXX Hack: This should be part of BuilderApplication
        if options.include_support_code is None:
            options.include_support_code = cf.include_support_code
        if options.resource is None:
            if not cf.default_collection:
                self.error("no resource to package specified")
            options.resource = cf.default_collection
        if not options.release_name:
            options.release_name = cf.release_name

        pkgs = sets.Set()
        for pkgname, location in options.support_packages:
            pkgs.add(pkgname)
        for pkgname, location in cf.support_packages.iteritems():
            if pkgname not in pkgs:
                options.support_packages.append((pkgname, location))
                pkgs.add(pkgname)

    def error(self, message, rc=1):
        self.logger.critical(message)
        sys.exit(rc)


class BuilderApplication(Application):

    def __init__(self, options):
        Application.__init__(self, options)
        self.manifests = []
        self.ip = None
        self.resource = options.resource
        # Create a new directory for all temporary files to go in:
        self.tmpdir = tempfile.mkdtemp(prefix=options.program + "-")
        self.old_tmpdir = tempfile.tempdir
        tempfile.tempdir = self.tmpdir
        if options.revision_tag:
            self.loader = loader.Loader(tag=options.revision_tag)
        else:
            self.loader = loader.Loader()
        self.ip = include.InclusionProcessor(self.loader)

        if self.resource not in self.locations:
            self.error("unknown resource: %s" % self.resource)
        self.resource_url = self.locations[self.resource]
        #
        release_name = options.release_name or self.resource
        self.target_name = "%s-%s" % (release_name, self.options.version)
        self.target_file = self.target_name + ".tgz"
        if self.options.tree_only:
            self.destination = os.path.abspath(self.target_name)
        else:
            self.destination = os.path.join(self.tmpdir, self.target_name)
        os.mkdir(self.destination)
        pkgs = sets.Set()
        self.support_packages = []
        for pkgname, location in options.support_packages:
            if pkgname not in pkgs:
                self.support_packages.append((pkgname, location))
        for pkgname, location in DEFAULT_SUPPORT_PACKAGES:
            if pkgname not in pkgs:
                self.support_packages.append((pkgname, location))
                pkgs.add(pkgname)
        for pkg in options.exclude_packages:
            self.exclude_packages.add(pkg)

    def build_distribution(self):
        """Create the distribution tree.

        This method does everything needed to knit a distribution
        together; it should be refactored substantially.
        """
        dep_sources = {}
        top = self.get_component(self.resource, self.resource_url)
        top.write_package(self.destination)
        distclass = self.options.distribution_class
        if self.options.collect:
            depsdir = os.path.join(self.destination, "Dependencies")
            first = True
            handled = self.exclude_packages.copy()
            handled.add(self.resource)
            remaining = top.get_dependencies() - handled
            while remaining:
                resource = remaining.pop()
                handled.add(resource)
                if resource not in self.locations:
                    # it's an external dependency, so we do nothing for now
                    self.logger.error(
                        "ignoring resource %r (no source) from %s"
                        % (resource, dep_sources.get(resource)))
                    continue
                #
                location = self.locations[resource]
                self.logger.debug("loading resource %r from %s",
                                  resource, location)
                component = self.get_component(resource, location)
                if first:
                    os.mkdir(depsdir)
                    first = False
                deps = component.get_dependencies()
                for d in deps - handled:
                    dep_sources[d] = resource
                remaining |= (deps - handled)
                fullname = ("%s-%s-%s"
                            % (resource, top.name, self.options.version))
                destination = os.path.join(depsdir, fullname)
                self.add_manifest(destination)
                component.write_package(destination)
                component.write_setup_py(pathparts=["..", ".."],
                                         distclass=distclass)
                component.write_setup_cfg()
        if self.options.application:
            top.write_setup_py(filename="install.py",
                               version=self.options.version,
                               distclass=distclass)
            self.write_application_support(top)
        else:
            top.write_setup_py(version=self.options.version,
                               distclass=distclass)
        top.write_setup_cfg()

    def get_component(self, resource, location):
        try:
            source = self.ip.loader.load(location)
            if os.path.isfile(source):
                return ModuleComponent(resource, location, source, self.ip)
            return PackageComponent(resource, location, source, self.ip)
        except zpkgtools.Error, e:
            self.error(str(e), rc=1)

    def add_manifest(self, destination):
        self.ip.add_manifest(destination)
        self.ip.add_output(os.path.join(destination, "MANIFEST"))
        self.manifests.append(destination)

    def write_manifests(self):
        # We sort and reverse the list of destinations to make sure
        # nested directories are handled before outer directories.
        self.manifests.sort()
        self.manifests.reverse()
        for dest in self.manifests:
            manifest = self.ip.drop_manifest(dest)
            # XXX should check whether MANIFEST exists already; how to handle?
            f = file(os.path.join(dest, "MANIFEST"), "w")
            for name in manifest:
                print >>f, name
            f.close()

    def write_application_support(self, component):
        pubinfo = component.get_publication_info()
        metavars = {
            "PACKAGE_FULL_NAME": pubinfo.name or component.name,
            "PACKAGE_SHORT_NAME": component.name,
            "PACKAGE_VERSION": self.options.version,
            }
        appsupport = os.path.join(zpkgtools.__path__[0], "appsupport")
        readme_txt = os.path.join(self.destination, "README.txt")
        if not os.path.exists(readme_txt):
            self.copy_template(appsupport, "README.txt", metavars)
        self.copy_template(appsupport, "configure", metavars)
        self.copy_template(appsupport, "Makefile.in", metavars)

    def copy_template(self, sourcedir, name, metavars):
        template = os.path.join(sourcedir, name) + ".in"
        output = os.path.join(self.destination, name)
        self.ip.add_output(output)
        f = open(template, "rU")
        text = f.read()
        f.close()
        for var in metavars:
            text = text.replace("@%s@" % var, metavars[var])
        f = open(output, "w")
        f.write(text)
        f.close()
        shutil.copymode(template, output)

    def include_support_code(self):
        """Include any support code needed by the generated setup.py.

        This will add the ``zpkgsetup`` package to the Support
        directory, but they won't be added to the set of packages that
        will be installed by the resulting distribution.
        """
        cleanup = False
        if self.options.revision_tag and self.options.revision_tag != "HEAD":
            # we really don't want the tagged version of the support code
            old_loader = self.loader
            self.loader = loader.Loader("HEAD")
            cleanup = True
        supportdest = os.path.join(self.destination, "Support")
        os.mkdir(supportdest)
        self.add_manifest(supportdest)
        for name, fallback_url in self.support_packages:
            self.include_support_package(name, fallback_url)
        if cleanup:
            self.loader.cleanup()
            self.loader = old_loader
        source = os.path.join(zpkgtools.__path__[0], "support")
        dest = os.path.join(self.destination, "Support")
        files = os.listdir(source)
        for fn in setup.filter_names(files):
            self.ip.copy_file(os.path.join(source, fn),
                              os.path.join(dest, fn))

    def include_support_package(self, name, fallback):
        """Add the support package `name` to the output directory.

        :Parameters:
          - `name`:  The name of the package to include.

          - `fallback`: Location to use if the package isn't found
            anywhere else.  This will typically be a cvs: URL.

        If a directory named `name` is already present in the output
        tree, it is left unchanged.
        """
        destination = os.path.join(self.destination, "Support", name)
        if os.path.exists(destination):
            # have the package as a side effect of something else
            return
        source = None
        url = fallback or self.locations.get(name)
        if not url:
            self.logger.warning("resource %s not configured;"
                                " no location known" % name)
            return
        if source is None:
            self.logger.debug("loading resource '%s' from %s",
                              name, url)
            source = self.loader.load_mutable_copy(url)

        self.ip.copyTree(source, destination)

    def create_tarball(self):
        """Generate a compressed tarball from the destination tree.

        The completed tarball is copied to the current directory.
        """
        pwd = os.getcwd()
        os.chdir(self.tmpdir)
        cmdline1 = ("tar", "czf", self.target_file,
                    "--owner=0", "--group=0", "--mode=a+r",
                    self.target_name)
        cmdline2 = ("tar", "czf", self.target_file, self.target_name)
        # The os.spawn?p*() functions are not available on Windows, so
        # we need to search the PATH ourselves:
        cmdpath = runlog.find_command(cmdline1[0])
        runlog.report_command(" ".join(cmdline1))
        try:
            rc = os.spawnv(os.P_WAIT, cmdpath, cmdline1)
            if os.WIFEXITED(rc) and os.WEXITSTATUS(rc) > 0:
                # didn't like the command line; maybe not GNU tar?
                if os.path.exists(self.target_file):
                    os.unlink(self.target_file)
                    cmdpath = runlog.find_command(cmdline2[0])
                runlog.report_exit_code(rc)
                runlog.report_command(" ".join(cmdline2))
                rc = os.spawnv(os.P_WAIT, cmdpath, cmdline2)
        finally:
            os.chdir(pwd)
        runlog.report_exit_code(rc)
        if rc:
            self.error("error generating %s" % self.target_file)
        # We have a tarball; clear some space, then copy the tarball
        # to the current directory:
        rmtree_force(self.destination)
        shutil.copy(os.path.join(self.tmpdir, self.target_file),
                    self.target_file)

    def cleanup(self):
        """Remove all temporary data storage."""
        rmtree_force(self.tmpdir)
        if self.tmpdir == tempfile.tempdir:
            tempfile.tempdir = self.old_tmpdir

    def run(self):
        """Run the application, using the other methods of the
        ``BuilderApplication`` object.
        """
        try:
            self.add_manifest(self.destination)
            try:
                # We have to include the support code first since
                # build_distribution() is going to write out the
                # top-level MANIFEST file.
                if self.options.include_support_code:
                    self.include_support_code()
                self.build_distribution()
            except zpkgtools.LoadingError, e:
                self.error(str(e), e.exitcode)
            self.write_manifests()
            if not self.options.tree_only:
                self.create_tarball()
            self.cleanup()
        except:
            print >>sys.stderr, "----\ntemporary files are in", self.tmpdir
            raise


class PackageComponent:
    """Regular Python package
    """

    def __init__(self, name, url, source, ip):
        self.name = name
        self.url = url
        self.ip = ip
        self.dependencies = None
        self.destination = None
        self.pkginfo = None
        self.pubinfo = None
        self.source = source
        specs = include.load(self.source)
        if specs.loads:
            source = self.ip.loader.load_mutable_copy(self.url)
            if source != self.source:
                self.source = source
                # we need to re-load the specs to get the .source
                # attribute of the specification objects correct
                # XXX need test!
                specs = include.load(source)
            self.ip.addIncludes(self.source, specs.loads)
        specs.collection.cook()
        specs.distribution.cook()
        self.collection = specs.collection
        self.distribution = specs.distribution
        #
        # Check that this package is valid:
        #
        if self.is_python_package() or self.has_packaging_data():
            return
        raise zpkgtools.Error(
            "%r is an invalid distribution component: all components must"
            " either be a Python package or provide a %s file"
            % (name, package.PACKAGE_CONF))

    def get_dependencies(self):
        """Get the direct dependencies of this component.

        :return: A set of the dependencies.
        :rtype: `sets.Set`

        For Python packages, the implied dependency on the parent
        package is made explicit.
        """
        if self.dependencies is None:
            deps_file = os.path.join(self.source, "DEPENDENCIES.cfg")
            if os.path.isfile(deps_file):
                f = open(deps_file, "rU")
                try:
                    self.dependencies = dependencies.load(f)
                finally:
                    f.close()
            else:
                self.dependencies = sets.Set()
            if self.is_python_package() and "." in self.name:
                self.dependencies.add(self.name[:self.name.rfind(".")])
        return self.dependencies

    def get_package_info(self):
        if self.pkginfo is None:
            destdir = os.path.join(self.destination, self.name)
            if self.is_python_package():
                pkginfo = package.loadPackageInfo(self.name, destdir,
                                                  self.name)
            else:
                pkginfo = package.loadCollectionInfo(destdir, self.name)
            self.pkginfo = pkginfo
        return self.pkginfo

    def get_publication_info(self):
        if self.pubinfo is None:
            pubinfo_file = os.path.join(self.source,
                                        publication.PUBLICATION_CONF)
            if os.path.isfile(pubinfo_file):
                f = open(pubinfo_file, "rU")
                try:
                    self.pubinfo = publication.load(f)
                finally:
                    f.close()
        return self.pubinfo

    def is_python_package(self):
        """Return True if this component represents a Python package."""
        if self.destination:
            dir = os.path.join(self.destination, self.name)
        else:
            dir = self.source
        return os.path.isfile(os.path.join(dir, "__init__.py"))

    def has_packaging_data(self):
        """Return True if this component contains packaging metadata."""
        # Should PUBLICATION.cfg count toword this?
        dir = self.source
        for fn in (package.PACKAGE_CONF,
                   include.PACKAGE_CONF,
                   "DEPENDENCIES.cfg"):
            if os.path.isfile(os.path.join(dir, fn)):
                return True
        return False

    def write_package(self, destination):
        self.destination = destination
        if not os.path.exists(destination):
            os.mkdir(destination)
        self.ip.addIncludes(destination, self.distribution)
        pkgdir = os.path.join(destination, self.name)
        self.ip.createDistributionTree(pkgdir, self.collection)
        # Be sure the packaging metadata is available, no matter what
        # PACKAGE.cfg says; we'll need when we use the distribution.
        # The DEPENDENCIES.cfg file is handled separately.
        for metafile in (package.PACKAGE_CONF,
                         publication.PUBLICATION_CONF,
                         "DEPENDENCIES.cfg"):
            dstname = os.path.join(destination, self.name, metafile)
            srcname = os.path.join(self.source, metafile)
            if os.path.exists(srcname) and not os.path.exists(dstname):
                self.ip.copy_file(srcname, dstname)

    def write_setup_cfg(self):
        setup_cfg = os.path.join(self.destination, "setup.cfg")
        self.ip.add_output(setup_cfg)
        pkginfo = self.get_package_info()
        f = open(setup_cfg, "w")
        f.write("# THIS IS A GENERATED FILE.\n")
        f.write("\n")
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

    def write_setup_py(self, filename="setup.py", version=None, pathparts=[],
                       distclass=None):
        setup_py = os.path.join(self.destination, filename)
        self.ip.add_output(setup_py)
        f = open(setup_py, "w")
        if pathparts:
            extrapath = ", ".join([""] + [repr(pp) for pp in pathparts])
        else:
            extrapath = ""
        print >>f, SETUP_HEADER % extrapath
        print >>f, "context = zpkgsetup.setup.SetupContext("
        if distclass:
            print >>f, "    %r, %r, __file__," % (self.name, version)
            print >>f, "    %r)" % distclass
        else:
            print >>f, "    %r, %r, __file__)" % (self.name, version)
        print >>f
        print >>f, "context.initialize()"
        print >>f, "context.setup()"
        f.close()


class ModuleComponent:
    """Component representing a top-level module
    """

    def __init__(self, name, url, source, ip):
        self.name = name
        self.url = url
        self.ip = ip
        self.dependencies = None
        self.destination = None
        self.pkginfo = None
        self.pubinfo = None
        self.source = source
        self.filename = os.path.basename(source)
        specs = include.load(self.source)
        specs.collection.cook()
        specs.distribution.cook()
        self.collection = specs.collection
        self.distribution = specs.distribution
        #
        # Check that this package is valid:
        #
        if not self.is_python_package():
            raise zpkgtools.Error(
                "%r is an invalid distribution component: all components must"
                " either be a Python package or provide a %s file"
                % (name, package.PACKAGE_CONF))

    def get_dependencies(self):
        """Get the direct dependencies of this component.

        :return: A set of the dependencies.
        :rtype: `sets.Set`

        We simply rule that top-level modules have no dependencies.
        At least we have no way of knowing.
        """
        self.dependencies = sets.Set()
        return self.dependencies

    def get_package_info(self):
        return self.pkginfo

    def get_publication_info(self):
        return self.pubinfo

    def is_python_package(self):
        """Return True if this component represents a Python package."""
        if self.destination:
            filename = os.path.join(self.destination, self.filename)
        else:
            filename = self.source
        return os.path.isfile(filename)

    def has_packaging_data(self):
        """Return True if this component contains packaging metadata.

        For top-level modules, we simply rule that the have no
        packaging metadata. They just want to be installed, basta."""
        return False

    def write_package(self, destination):
        self.destination = destination
        if not os.path.exists(destination):
            os.mkdir(destination)
        self.ip.addIncludes(destination, self.distribution)
        self.ip.copy_file(self.source, destination)

    def write_setup_cfg(self):
        setup_cfg = os.path.join(self.destination, "setup.cfg")
        self.ip.add_output(setup_cfg)
        f = open(setup_cfg, "w")
        f.write("# THIS IS A GENERATED FILE.\n")
        f.write("\n")
        f.write("[install_lib]\n")
        # generate .pyc files
        f.write("compile = 1\n")
        # generate .pyo files using "python -O"
        f.write("optimize = 1\n")
        f.close()

    def write_setup_py(self, filename="setup.py", version=None, pathparts=[],
                       distclass=None):
        # simply assume that the filename ends in '.py'
        module_name = self.filename[:-3]
        setup_py = os.path.join(self.destination, filename)
        self.ip.add_output(setup_py)
        f = open(setup_py, "w")
        if pathparts:
            extrapath = ", ".join([""] + [repr(pp) for pp in pathparts])
        else:
            extrapath = ""
        print >>f, SETUP_HEADER % extrapath
        print >>f, "context = zpkgsetup.setup.SetupContext("
        if distclass:
            print >>f, "    %r, %r, __file__," % (module_name, version)
            print >>f, "    %r)" % distclass
        else:
            print >>f, "    %r, %r, __file__)" % (module_name, version)
        print >>f
        print >>f, "context.initialize()"
        print >>f, "context.setup()"
        f.close()


SETUP_HEADER = """\
#! /usr/bin/env python
#
# THIS IS A GENERATED FILE.  DO NOT EDIT THIS DIRECTLY.

# Add the Support/ directory to sys.path to get our support code:
#
import os
import sys

try:
    __file__
except NameError:
    # Python 2.2.x does not have __file__ for scripts.
    __file__ = sys.argv[0]

here = os.path.dirname(os.path.realpath(__file__))
support_dir = os.path.join(here%s, 'Support')
support_dir = os.path.normpath(support_dir)
if os.path.isdir(support_dir):
    sys.path.insert(0, support_dir)

import zpkgsetup.setup

"""


def version_from_tagname(tagname):
    """Compute a version number based on a revision control tag.

    :param tagname: The name of the tag to convert.
    :return: A version number for a release.
    """
    parts = tagname.split("-")
    version = parts[-1].replace("_", ".")
    m = re.match(r"\d+(\.\d+){1,3}(?:[a-z]+\d*)?$", version)
    if m is None:
        return None
    else:
        return version


def parse_args(argv):
    """Parse the command line, return an options object and the
    identifier of the resource to be packaged.

    :return: Options object containing values derived from the command
      line, including the name of the application and the name of the
      resource to operate on.

    :param argv: The command line arguments, including argv[0].

    """

    prog = os.path.basename(argv[0])
    parser = optparse.OptionParser(
        prog=prog,
        usage="usage: %prog [options] resource",
        version="%prog 0.1")

    # "global" options:
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

    # options specific to building a package:
    parser.add_option(
        "-a", "--application", dest="application",
        action="store_true",
        help="build an application distribution")
    parser.add_option(
        "-c", "--collection", dest="collect",
        action="store_true",
        help="collect dependencies into the distribution")
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
        "-t", "--tree", dest="tree_only", action="store_true",
        help="generate an unpacked distribution tree, not a tarball")
    parser.add_option(
        "-v", dest="version",
        help="version label for the new distribution")
    parser.add_option(
        "--support", dest="support_packages", action="append",
        default=[],
        help="name additional support package resource", metavar="RESOURCE")
    parser.add_option(
        "--distribution", dest="distribution_class",
        help="name of the distribution class", metavar="CLASS")
    parser.add_option(
        "-x", "--exclude", dest="exclude_packages", action="append",
        default=[], metavar="PACKAGE",
        help=("resource to exclude the from distribution"
              " (dependencies will be ignored)"))

    options, args = parser.parse_args(argv[1:])
    if len(args) > 1:
        parser.error("too many arguments")
    try:
        for exclusion in options.exclude_packages:
            config.resource_name(exclusion)
    except ValueError, e:
        parser.error(str(e))
    options.program = prog
    options.args = args
    options.support_packages = [
        (pkgname, None) for pkgname in options.support_packages]
    if args:
        options.resource = args[0]
    else:
        options.resource = None
    if options.revision_tag and not options.version:
        options.version = version_from_tagname(options.revision_tag)
    if not options.version:
        options.version = "0.0.0"
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
        if e.code is None or isinstance(e.code, int):
            return 0
        else:
            print >>sys.stderr, e
            return 2

    try:
        app = BuilderApplication(options)
        app.run()
    except SystemExit, e:
        return e.code
    except KeyboardInterrupt:
        return 1
    else:
        return 0
