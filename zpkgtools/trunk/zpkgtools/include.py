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
"""Processor for inclusions when building a release.

:Variables:
  - `PACKAGE_CONF`: The name of the file that specifies how the
    package is assembled.

"""

import glob
import os
import posixpath
import shutil
import urllib

from zpkgsetup import cfgparser
from zpkgsetup import loggingapi as logging
from zpkgsetup import publication
from zpkgsetup import setup
from zpkgsetup import urlutils

from zpkgtools import Error
from zpkgtools import loader


logger = logging.getLogger(__name__)

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

    def __str__(self):
        s = InclusionError.__str__(self)
        if self.filename:
            s = "%s\n(in %s" % (s, self.filename)
            if self.lineno is not None:
                s = "%s, line %d" % (s, self.lineno)
            s += ")"
        return s


def load(sourcedir, url=None):
    """Return the specifications for populating the distribution and
    collection directories.

    :param sourcedir: Directory we're loading the specifications for.

    :param url: URL used to retrieve `sourcedir`; this is needed to
      resolve repository: references.

    If there is not specification file, return empty specifications.
    """
    package_conf = os.path.join(sourcedir, PACKAGE_CONF)
    schema = SpecificationSchema(sourcedir, package_conf, baseurl=url)
    if os.path.isfile(package_conf):
        f = open(package_conf, "rU")
        try:
            parser = cfgparser.Parser(f, package_conf, schema)
            config = parser.load()
        finally:
            f.close()
        if config.collection.excludes:
            # XXX should make sure PACKAGE_CONF isn't already excluded
            config.collection.excludes.append(PACKAGE_CONF)
        elif not config.collection.includes:
            # Nothing included or excluded; simply exclude PACKAGE_CONF:
            config.collection.excludes.append(PACKAGE_CONF)
    else:
        config = schema.getConfiguration()
    return config


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
    if posixpath.isabs(np) or np.split("/", 1)[0] == "..":
        raise InclusionSpecificationError(
            "%s path must not be absolute or refer to a location"
            " not contained in the source directory"
            % path)
    if np == ".":
        return os.curdir
    else:
        return np.replace("/", os.sep)


def normalize_path_or_url(path, type, group, baseurl=None):
    if ":" in path:
        scheme, rest = urllib.splittype(path)
        if len(scheme) != 1:
            # should normalize the URL, but skip that for now
            if baseurl and scheme == "repository":
                path = loader.join(baseurl, path)
            return path
    return normalize_path(path, type, group)


class SpecificationSchema(cfgparser.Schema):
    """Specialized schema that handles populating a set of Specifications.
    """

    def __init__(self, source, filename, baseurl=None):
        self.baseurl = baseurl
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
        if child.includes and child.excludes:
            # XXX not sure what the exact semantics should be of
            # allowing both inclusions and exclusions at the same
            # time; which takes precedence?  what about precedence
            # when wildcards are involved?
            raise cfgparser.ConfigurationError(
                "exclusions and inclusions cannot coexist in a single section")

    def createSection(self, name, typename, typedef):
        raise NotImplementedError(
            "createSection() should not be called for SpecificationSchema")

    def finishSection(self, section):
        return section

    def addValue(self, section, workfile, other):
        if not isinstance(section, Specification):
            raise cfgparser.ConfigurationError(
                "all inclusion lines must be in a section")

        if other == "-":
            # This is an exclusion.
            if section.group != "collection":
                raise cfgparser.ConfigurationError(
                    "exclusions are only permitted in <collection>")
            workfile = normalize_path(workfile, "exclusion", section.group)
            section.excludes.append(workfile)
            return

        if section.group == "load":
            if not other:
                raise cfgparser.ConfigurationError(
                    "referenced file must be named explicitly"
                    " in <load> section")
            # perhaps should make sure workfile and other don't refer
            # to the same file
            other = normalize_path_or_url(other, "source", section.group,
                                          self.baseurl)
        elif other:
            # workfile and other have a backward relationship for this:
            # <destination>
            #   target workfile
            # </destination>
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

      - `excludes`: List of relative paths (relative to the source)
        which should *not* be copied along with the included files.

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
        self.excludes = []
        self.source = source
        self.filename = filename
        self.group = group

    def __nonzero__(self):
        return bool(self.includes or self.excludes)

    def cook(self):
        patterns = self.includes.pop(None, [])
        source = os.path.normpath(self.source)
        prefix = os.path.join(source, "")
        for pat in patterns:
            path = os.path.join(source, pat)
            expansions = setup.filter_names(glob.glob(path))
            if not expansions:
                raise InclusionSpecificationError(
                    "%r doesn't match any files in <%s>" % (pat, self.group),
                    self.filename)
            for fn in expansions:
                suffix = fn[len(prefix):].replace(os.sep, "/") # POSIX form
                self.includes[suffix] = suffix
        excludes = []
        for pat in self.excludes:
            path = os.path.join(source, pat)
            expansions = setup.filter_names(glob.glob(path))
            if not expansions:
                raise InclusionSpecificationError(
                    "%r doesn't match any files in <%s>" % (pat, self.group),
                    self.filename)
            for fn in expansions:
                suffix = fn[len(prefix):].replace(os.sep, "/") # POSIX form
                if suffix not in excludes:
                    excludes.append(suffix)
        self.excludes[:] = excludes


class InclusionProcessor:
    """Handler for processing inclusion specifications.

    Methods are provided for managing manifest lists and creating
    the output tree.

    """
    def __init__(self, loader):
        """Initialize the processor.

        :param loader: Resource loader which should be used to load
          external resources.

        """
        self.manifests = []
        self.loader = loader

    def createDistributionTree(self, destination, spec):
        """Create the output tree according to `spec`.

        :Parameters:
          - `destination`: Path of the top-level output directory.
            This directory will be created if it doesn't exist.

          - `spec`: ``Specification`` object that describes what to
            include.  If omitted, an empty specification is used.

        """
        destination = os.path.abspath(destination)
        if spec.includes:
            self.create_directory(spec.source, destination)
            self.addIncludes(destination, spec)
        else:
            self.copyTree(spec.source, destination, spec.excludes,
                          nested=False)

    def copyTree(self, source, destination, excludes=(), nested=True):
        """Populate the destination tree from the source tree.

        :Parameters:
          - `source`: Absolute path to a directory to copy into the
            destination tree.

          - `destination`: Absolute path to a directory that
            corresponds to the `source` tree.  It will be created if
            it doesn't exist.

          - `excludes`: Paths relative to source which should be
            excluded from the copy operation.

        Files and directories will be created with the same permission
        bits and stat info as the source tree.
        """
        # The `nested` flag is only for internal use; it should be
        # False only when calling copyTree based on a specification
        # object represented by a PACKAGE_CONF file located in the
        # directory identified by `source`.  For any other call,
        # `nested` should be True since PACKAGE_CONF files need to be
        # processed.

        self.create_directory(source, destination)
        prefix = os.path.join(source, "")

        # The directory walk *must* be performed in top-down fashion
        # since the handling of nested PACKAGE_CONF files must be able
        # to modify the list of directories which are considered.
        #
        for dirname, dirs, files in os.walk(source, topdown=True):
            dirs[:] = setup.filter_names(dirs)
            files = setup.filter_names(files)

            # reldir is the name of the directory to write to,
            # relative to destination.  It will be '' at the top
            # level.
            reldir = dirname[len(prefix):]
            if reldir:
                destdir = os.path.join(destination, reldir)
            else:
                destdir = destination

            if PACKAGE_CONF in files and ((dirname != source) or nested):
                # a nested PACKAGE.cfg needs to be handled as well
                specs = load(dirname)
                if specs.loads:
                    raise InclusionSpecificationError(
                        "<load> disallowed in a nested %s file"
                        % PACKAGE_CONF)
                if specs.collection:
                    specs.collection.cook()
                    self.createDistributionTree(destdir, specs.collection)
                    # Don't recurse into any directories here; those
                    # were handled by the inner call to
                    # self.createDistributionTree().
                    del dirs[:]
                    continue

            if excludes:
                # excludes are in POSIX path notation
                preldir = reldir.replace(os.sep, "/")
                for name in dirs[:]:
                    prelpath = posixpath.join(preldir, name)
                    if prelpath in excludes:
                        dirs.remove(name)
                for name in files[:]:
                    prelpath = posixpath.join(preldir, name)
                    if prelpath in excludes:
                        files.remove(name)

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
                self.create_directory(srcname, destname)

    def create_directory(self, source, destination):
        if not os.path.exists(destination):
            # Create the directory, copying over the permission
            # bits and stat info.
            os.mkdir(destination)
            shutil.copymode(source, destination)

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
        logger.debug("processing <%s> from %s (dest = %s)",
                     spec.group, spec.filename, destination)
        for source, relpath in spec.includes.iteritems():
            self.addSingleInclude(relpath, source, destination, spec.source)

    def addSingleInclude(self, relpath, source, destination, dir):
        """Process a single include specification line.

        :Parameters:
          - `relpath`: Path relative to the destination directory, as
            taken from the specification.  This should use the path
            notation of the host operating system.

          - `source`: Path or URL to the input file or directory.

          - `destination`: Top-level destination directory; this is
            used as a base directory for `relpath`.

        """
        logger.debug("adding include %s from %s (dest = %s)",
                     relpath, source, destination)
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
            source = urlutils.file_url(os.path.join(dir, source))
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
