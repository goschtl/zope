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
"""Processor for inclusions when building a release.

:Variables:
  - `EXCLUDE_NAMES`: Names of files and directories that will be
    excluded from copying.  These are generally related to source
    management systems, but don't need to be.

  - `EXCLUDE_PATTERNS`: Glob patterns used to filter the set of files
    that are copied.  Any file with a name matching these patterns
    will be ignored.

  - `PACKAGE_CONF`: The name of the file that specifies how the
    package is assembled.

"""

import fnmatch
import glob
import os
import posixpath
import shutil
import urllib

from zpkgtools import Error

from zpkgtools import cfgparser
from zpkgtools import publication


# Names that are exluded from globbing results:
EXCLUDE_NAMES = ["CVS", ".cvsignore", "RCS", "SCCS", ".svn"]
EXCLUDE_PATTERNS = ["*.py[cdo]", "*.s[ol]", ".#*", "*~"]

# Name of the configuration file:
PACKAGE_CONF = "PACKAGE.cfg"


class InclusionError(Error):
    """Raised to indicate errors processing inclusions."""


class InclusionSpecificationError(cfgparser.ConfigurationError,
                                  InclusionError):
    """Raised to indicate errors in an inclusion specification."""

    def __init__(self, message, filename=None, lineno=None):
        InclusionError.__init__(self, message)
        cfgparser.ConfigurationError.__init__(self, message)
        self.filename = filename
        self.lineno = lineno


def load(sourcedir):
    """Return the specifications for populating the distribution and
    collection directories.

    If there is not specification file, return empty specifications.
    """
    package_conf = os.path.join(sourcedir, PACKAGE_CONF)
    schema = SpecificationSchema(sourcedir, package_conf)
    if os.path.isfile(package_conf):
        f = open(package_conf, "rU")
        try:
            parser = cfgparser.Parser(f, package_conf, schema)
            config = parser.load()
        finally:
            f.close()
    else:
        config = schema.getConfiguration()
    return config


def filter_names(names):
    """Given a list of file names, return those names that should be copied.
    """
    names = [n for n in names
             if n not in EXCLUDE_NAMES]
    # This is needed when building a distro from a working
    # copy (likely a checkout) rather than a pristine export:
    for pattern in EXCLUDE_PATTERNS:
        names = [n for n in names
                 if not fnmatch.fnmatch(n, pattern)]
    return names


def normalize_path(path, type, group):
    if ":" in path:
        scheme, rest = urllib.splittype(path)
        if len(scheme) == 1:
            # looks like a drive letter for Windows; scream,
            # 'cause that's not allowable:
            raise InclusionSpecificationError(
                "drive letters are not allowed in inclusions: %r" % path)
        else:
            raise InclusionSpecificationError(
                "URLs are not allowed in inclusions")
    np = posixpath.normpath(path)
    if posixpath.isabs(np) or np[:1] == ".":
        raise InclusionSpecificationError(
            "%s path must not be absolute or refer to a location"
            " not contained in the source directory"
            % path)
    return np.replace("/", os.sep)


def normalize_path_or_url(path, type, group):
    if ":" in path:
        scheme, rest = urllib.splittype(path)
        if len(scheme) != 1:
            # should normalize the URL, but skip that for now
            return path
    return normalize_path(path, type, group)


class SpecificationSchema(cfgparser.Schema):
    """Specialized schema that handles populating a set of Specifications.
    """

    def __init__(self, source, filename):
        self.filename = filename
        self.source = source

    def getConfiguration(self):
        conf = cfgparser.SectionValue(None, None, None)
        conf.loads = Specification(
            self.source, self.filename, "load")
        conf.collection = Specification(
            self.source, self.filename, "collection")
        conf.distribution = Specification(
            self.source, self.filename, "distribution")
        return conf

    def startSection(self, parent, typename, name):
        if not isinstance(parent, cfgparser.SectionValue):
            raise cfgparser.ConfigurationError("unexpected section")
        if typename == "collection":
            return parent.collection
        elif typename == "distribution":
            return parent.distribution
        elif typename == "load":
            return parent.loads
        raise cfgparser.ConfigurationError("unknown section type: %s"
                                           % typename)

    def endSection(self, parent, typename, name, child):
        pass

    def createSection(self, name, typename, typedef):
        raise NotImplementedError(
            "createSection() should not be called for SpecificationSchema")

    def finishSection(self, section):
        return section

    def addValue(self, section, workfile, other):
        if not isinstance(section, Specification):
            raise cfgparser.ConfigurationError(
                "all inclusion lines must be in a section")

        if section.group == "load":
            if not other:
                raise cfgparser.ConfigurationError(
                    "referenced file must be named explicitly"
                    " in <load> section")
            # perhaps should make sure workfile and other don't refer
            # to the same file
            other = normalize_path_or_url(other, "source", section.group)
        elif other:
            other = normalize_path(other, "destination", section.group)

        if workfile:
            workfile = normalize_path(workfile, "workspace file",
                                      section.group)

        if other:
            section.includes[other] = workfile
        else:
            L = section.includes.setdefault(None, [])
            L.append(workfile)


class Specification:
    """Specification for files to include.

    :Ivariables:
      - `includes`: Mapping from relative path (relative to the
        source) to either the destination path (relative) or an empty
        string.

      - `source`: Source directory which will be used to expand glob
        patterns.

      - `filename`: Path of the file from which this specification was
        loaded.  This is used when reporting errors.

      - `group`: String indicating which section of the specification
        file was used to generate this specification.

    """

    def __init__(self, source, filename, group):
        """Initialize the Specification object.

        :Parameters:
          - `source`: Directory that will serve as the primary source
            directory; this is needed to support filename globbing.

          - `filename`: Path of the file from which this specification
            was loaded.  This is used when reporting errors.

          - `group`: String indicating which section of the
            specification file was used to generate this
            specification.

        """
        # The source directory is needed since globbing is performed
        # to locate files if the spec includes wildcards.
        self.includes = {}
        self.source = source
        self.filename = filename
        self.group = group

    def cook(self):
        patterns = self.includes.pop(None, [])
        source = os.path.normpath(self.source)
        prefix = os.path.join(source, "")
        for pat in patterns:
            path = os.path.join(source, pat)
            expansions = filter_names(glob.glob(path))
            if not expansions:
                raise InclusionSpecificationError(
                    "%r doesn't match any files in <%s>" % (pat, self.group),
                    self.filename)
            for fn in expansions:
                suffix = fn[len(prefix):]
                self.includes[suffix] = suffix


class InclusionProcessor:
    """Handler for processing inclusion specifications.

    Methods are provided for managing manifest lists and creating
    the output tree.

    """
    def __init__(self, source, loader):
        """Initialize the processor.

        :Parameters:
          - `source`: Source directory for the primary resource being
            included.

          - `loader`: Resource loader which should be used to load
            external resources.

        """
        if not os.path.exists(source):
            raise InclusionError("source directory does not exist: %r"
                                 % source)
        self.source = os.path.abspath(source)
        self.manifests = []
        self.loader = loader

    def createDistributionTree(self, destination, spec=None):
        """Create the output tree according to `spec`.

        :Parameters:
          - `destination`: Path of the top-level output directory.
            This directory will be created if it doesn't exist.

          - `spec`: ``Specification`` object that describes what to
            include.  If omitted, an empty specification is used.

        """
        if spec is None:
            spec = Specification(self.source, None, "collection")
        destination = os.path.abspath(destination)
        if spec.includes:
            if not os.path.exists(destination):
                os.mkdir(destination)
                shutil.copymode(spec.source, destination)
                shutil.copystat(spec.source, destination)
            self.addIncludes(destination, spec)
        else:
            self.copyTree(spec.source, destination)

    def copyTree(self, source, destination):
        """Populate the destination tree from the source tree.

        :Parameters:
          - `source`: Absolute path to a directory to copy into the
            destination tree.

          - `destination`: Absolute path to a directory that
            corresponds to the `source` tree.  It will be created if
            it doesn't exist.

        Files and directories will be created with the same permission
        bits and stat info as the source tree.
        """
        if not os.path.exists(destination):
            os.mkdir(destination)
            shutil.copymode(source, destination)
            shutil.copystat(source, destination)
        prefix = os.path.join(source, "")
        for dirname, dirs, files in os.walk(source, topdown=True):
            dirs[:] = filter_names(dirs)
            files = filter_names(files)

            # reldir is the name of the directory to write to,
            # relative to destination.  It will be '' at the top
            # level.
            reldir = dirname[len(prefix):]
            if reldir:
                destdir = os.path.join(destination, reldir)
            else:
                destdir = destination
            for file in files:
                srcname = os.path.join(dirname, file)
                destname = os.path.join(destdir, file)
                # Copy file data, permission bits, and stat info;
                # owner/group are not copied.
                self.copy_file(srcname, destname)

            for dir in dirs[:]:
                srcname = os.path.join(dirname, dir)
                destname = os.path.join(destdir, dir)
                if publication.PUBLICATION_CONF in os.listdir(srcname):
                    dirs.remove(dir)
                    continue
                # Create the directory, copying over the permission
                # bits and stat info.
                os.mkdir(destname)
                shutil.copymode(srcname, destname)
                shutil.copystat(srcname, destname)

    def copy_file(self, source, destination):
        """Copy a single file into the output tree."""
        shutil.copy2(source, destination)
        self.add_output(destination)

    def add_output(self, path):
        """Add `path` to each of the relevant manifests."""
        for prefix, manifest in self.manifests:
            if path.startswith(prefix):
                relpath = path[len(prefix):]
                parts = relpath.split(os.sep)
                if len(parts) == 1:
                    manifest.append(parts[0])
                else:
                    manifest.append(posixpath.join(*parts))

    # This pair of methods handles the creation and removal of
    # manifest lists.  We use this approach since we need to support
    # multiple manifests for collection distributions (each component
    # will have a manifest of it's own, as well as the package as a
    # whole).  This makes managing manifests a function of the client
    # rather than being implicit.

    def add_manifest(self, destination):
        prefix = os.path.join(destination, "")
        self.manifests.append((prefix, []))

    def drop_manifest(self, destination):
        prefix = os.path.join(destination, "")
        for i in range(len(self.manifests)):
            if self.manifests[i][0] == prefix:
                return self.manifests.pop(i)[1]
        raise ValueError("no manifest for %s" % destination)

    def addIncludes(self, destination, spec):
        """Process all the inclusion from a specification."""
        for source, relpath in spec.includes.iteritems():
            self.addSingleInclude(relpath, source, destination)

    def addSingleInclude(self, relpath, source, destination):
        """Process a single include specification line.

        :Parameters:
          - `relpath`: Path relative to the destination directory, as
            taken from the specification.  This should use the path
            notation of the host operating system.

          - `source`: Path or URL to the input file or directory.

          - `destination`: Top-level destination directory; this is
            used as a base directory for `relpath`.

        """
        dirname, basename = os.path.split(relpath)
        if dirname:
            destdir = os.path.join(destination, dirname)
            if not os.path.exists(destdir):
                os.makedirs(destdir)
        else:
            # Known to exist, so no need to create it.
            destdir = destination

        # This is what we want to create:
        destdir = os.path.join(destdir, basename)

        type = urllib.splittype(source)[0] or ''
        if len(type) in (0, 1):
            # figure it's a path ref, possibly w/ a Windows drive letter
            source = os.path.join(self.source, source)
            source = "file://" + urllib.pathname2url(source)
            type = "file"
        try:
            path = self.loader.load(source)
        except ValueError:
            # not a supported URL type
            raise InclusionError("cannot load from a %r URL" % type)
        self.includeFromLocalTree(path, destdir)

    def includeFromLocalTree(self, source, destination):
        # Check for file-ness here since copyTree() doesn't handle
        # individual files at all.
        if os.path.isfile(source):
            self.copy_file(source, destination)
        else:
            self.copyTree(source, destination)
