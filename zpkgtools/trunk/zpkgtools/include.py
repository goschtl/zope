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

"""

import fnmatch
import glob
import os
import posixpath
import shutil
import urllib
import urllib2

from zpkgtools import Error

from zpkgtools import cfgparser
from zpkgtools import cvsloader
from zpkgtools import publication


# Names that are exluded from globbing results:
EXCLUDE_NAMES = ["CVS", ".cvsignore", "RCS", "SCCS", ".svn"]
EXCLUDE_PATTERNS = ["*.py[cdo]", "*.s[ol]", ".#*", "*~"]

# Name of the configuration file:
PACKAGE_CONF = "PACKAGE.cfg"


class InclusionError(Error):
    pass


class InclusionSpecificationError(cfgparser.ConfigurationError, InclusionError):
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
        config.collection.excludes[package_conf] = package_conf
    else:
        config = schema.getConfiguration()
    return config.collection, config.distribution


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


def normalize_path(path, type):
    if ":" in path:
        scheme, rest = urllib.splittype(path)
        if len(scheme) == 1:
            # looks like a drive letter for Windows; scream,
            # 'cause that's not allowable:
            raise InclusionSpecificationError(
                "drive letters are not allowed in inclusions: %r" % path)
    np = posixpath.normpath(path)
    if posixpath.isabs(np) or np[:1] == ".":
        raise InclusionSpecificationError(
            "%s path must not be absolute or refer to a location"
            " not contained in the source directory"
            % path)
    return np.replace("/", os.sep)


def normalize_path_or_url(path, type):
    if ":" in path:
        scheme, rest = urllib.splittype(path)
        if len(scheme) != 1:
            # should normalize the URL, but skip that for now
            return path
    return normalize_path(path, type)


class SpecificationSchema(cfgparser.Schema):
    """Specialized schema that handles populating a pair of Specifications.
    """

    def __init__(self, source, filename):
        self.filename = filename
        self.source = source

    def getConfiguration(self):
        conf = cfgparser.SectionValue(None, None, None)
        conf.collection = self.collection = Specification(self.source)
        conf.distribution = self.distribution = Specification(self.source)
        return conf

    def startSection(self, parent, typename, name):
        if not isinstance(parent, cfgparser.SectionValue):
            raise cfgparser.ConfigurationError("unexpected section")
        if typename == "collection":
            return parent.collection
        elif typename == "distribution":
            return parent.distribution
        raise cfgparser.ConfigurationError("unknown section type: %s"
                                           % typename)
                                           
    def endSection(self, parent, typename, name, child):
        pass

    def createSection(self, name, typename, typedef):
        raise NotImplementedError(
            "createSection() should not be called for SpecificationSchema")

    def finishSection(self, section):
        return section

    def addValue(self, section, dest, src):
        if not isinstance(section, Specification):
            raise cfgparser.ConfigurationError(
                "all inclusion lines must be in a <collection> or"
                " <distribution> section")
        if not src:
            raise InclusionSpecificationError("source information omitted",
                                              self.filename)
        dest = normalize_path(dest, "destination")
        src = normalize_path_or_url(src, "source")
        if src == "-":
            if section is self.distribution:
                raise InclusionSpecificationError(
                    "cannot exclude files from the distribution root",
                    self.filename)
            path = os.path.join(self.source, dest)
            expansions = filter_names(glob.glob(path))
            if not expansions:
                raise InclusionSpecificationError(
                    "exclusion %r doesn't match any files" % dest,
                    self.filename)
            for fn in expansions:
                section.excludes[fn] = fn
        else:
            section.includes[dest] = src


class Specification:
    """Specification for files to include and exclude.

    :Ivariables:
      - `excludes`: Iterable containing the absolute path names of the
        files in the source tree that should not be part of the
        destination.

      - `includes`: Mapping from relative path (relative to the
        destination) to either an absolute path in the source
        directory or a URL.

    """

    # XXX Needing to pass the source directory to the constructor is a
    # bit of a hack, ...  A
    # better approach may be to have "raw" and "cooked" versions of
    # the specification object; the raw version would only have the
    # information loaded from a specification file, and the cooked
    # version would be (essentially) a list of directory creation and
    # file copy operations.  The input source directory would be a
    # parameter to the "cook" operation.

    def __init__(self, source):
        """Initialize the Specification object.

        :Parameters:
          - `source`: Directory that will serve as the primary source
            directory; this is needed to support exclusions.

        """
        # The source directory is needed since globbing is performed
        # to locate files if the spec includes wildcards.
        self.excludes = {}
        self.includes = {}
        self.source = source


class InclusionProcessor:
    """Handler for processing inclusion specifications.

    Methods are provided for managing manifest lists and creating
    the output tree.

    """
    def __init__(self, source, loader=None):
        if not os.path.exists(source):
            raise InclusionError("source directory does not exist: %r"
                                 % source)
        self.source = os.path.abspath(source)
        self.manifests = []
        if loader is None:
            loader = cvsloader.CvsLoader()
        self.cvs_loader = loader

    def createDistributionTree(self, destination, spec=None):
        """Create the output tree according to `spec`.

        :Parameters:
          - `destination`: Path of the top-level output directory.
            This directory will be created if it doesn't exist.

          - `spec`: ``Specification`` object that describes what to
            include and exclude.  If omitted, an empty specification
            is used.

        """
        if spec is None:
            spec = Specification(self.source)
        destination = os.path.abspath(destination)
        self.copyTree(spec.source, destination, spec.excludes)
        self.addIncludes(destination, spec)

    def copyTree(self, source, destination, excludes={}):
        """Populate the destination tree from the source tree.

        :Parameters:
          - `source`: Absolute path to a directory to copy into the
            destination tree.

          - `destination`: Absolute path to a directory that
            corresponds to the `source` tree.  It will be created if
            it doesn't exist.

          - `excludes`: Container for paths that should not be copied
            from the `source` tree.  This should be an absolute path.

        Files and directories will be created with the same permission
        bits and stat info as the source tree.

        Entries identified as exclusions will not be copied at all.
        """
        if not os.path.exists(destination):
            os.mkdir(destination)
            shutil.copymode(source, destination)
            shutil.copystat(source, destination)
        prefix = os.path.join(source, "")
        for dirname, dirs, files in os.walk(source, topdown=True):
            dirs[:] = filter_names(dirs)
            files = filter_names(files)

            # remove excluded directories:
            for dir in dirs[:]:
                fullpath = os.path.join(dirname, dir)
                if fullpath in excludes:
                    dirs.remove(dir)

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
                if srcname in excludes:
                    continue
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
        for relpath, source in spec.includes.iteritems():
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

        try:
            cvsurl = cvsloader.parse(source)
        except ValueError:
            # not a cvs: or repository: URL
            type, rest = urllib.splittype(source)
            if type:
                # some sort of URL
                self.includeFromUrl(source, destdir)
            else:
                # local path; perhaps this join should be handled by
                # the Specification to avoid having to keep
                # self.source around?
                self.includeFromLocalTree(os.path.join(self.source, source),
                                          destdir)
        else:
            if isinstance(cvsurl, cvsloader.RepositoryUrl):
                raise InclusionError("can't load from repository: URL")
            self.includeFromCvs(cvsurl, destdir)

    def includeFromLocalTree(self, source, destination):
        # Check for file-ness here since copyTree() doesn't handle
        # individual files at all.
        if os.path.isfile(source):
            self.copy_file(source, destination)
        else:
            self.copyTree(source, destination)

    def includeFromUrl(self, source, destination):
        # XXX treat FTP URLs specially to get permission bits and directories?
        inf = urllib2.urlopen(source)
        try:
            outf = open(destination, "w")
            try:
                shutil.copyfileobj(inf, outf)
            finally:
                outf.close()
            self.add_output(destination)
        finally:
            inf.close()

    def includeFromCvs(self, cvsurl, destination):
        source = self.cvs_loader.load(cvsurl.getUrl())
        self.includeFromLocalTree(source, destination)
