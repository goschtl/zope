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
"""Processor for inclusions when building a release."""

import fnmatch
import glob
import os
import posixpath
import shutil
import urllib
import urllib2

from zpkgtools import Error

from zpkgtools import cvsloader


# Names that are exluded from globbing results:
EXCLUDE_NAMES = ["CVS", ".cvsignore", "RCS", "SCCS", ".svn"]
EXCLUDE_PATTERNS = ["*.py[cdo]", "*.s[ol]"]


class InclusionError(Error):
    pass


class InclusionSpecificationError(ValueError, InclusionError):
    def __init__(self, message, filename, lineno):
        self.filename = filename
        self.lineno = lineno
        ValueError.__init__(self, message)


def filter_names(names):
    names = [n for n in names
             if n not in EXCLUDE_NAMES]
    # This is needed when building a distro from a working
    # copy (likely a checkout) rather than a pristine export:
    for pattern in EXCLUDE_PATTERNS:
        names = [n for n in names
                 if not fnmatch.fnmatch(n, pattern)]
    return names


class Specification:
    """Specification for files to include and exclude.

    The following attributes are provided:

    excludes
      Iterable containing the absolute path names of the files in the
      source tree that should not be part of the destination.

    includes
      Mapping from relative path (relative to the destination) to
      either an absolute path in the source directory or a URL.

    """

    def __init__(self, source):
        # The source directory is needed since globbing is performed
        # to locate files if the spec includes wildcards.
        self.excludes = {}
        self.includes = {}
        self.source = source

    def load(self, f, filename):
        lineno = 0
        for line in f:
            lineno += 1
            line = line.strip()
            if line[:1] in ("", "#"):
                continue
            parts = line.split(None, 1)
            if len(parts) != 2:
                raise InclusionSpecificationError(
                    "inclusion specifications require"
                    " both target and source parts",
                    filename, lineno)
            dest, src = parts
            dest = self.normalizePath(dest, "destination", filename, lineno)
            src = self.normalizePathOrURL(src, "source", filename, lineno)
            if src == "-":
                path = os.path.join(self.source, dest)
                expansions = filter_names(glob.glob(path))
                if not expansions:
                    raise InclusionSpecificationError(
                        "exclusion %r doesn't match any files" % dest,
                        filename, lineno)
                for fn in expansions:
                    self.excludes[fn] = fn
            else:
                self.includes[dest] = src

    def normalizePath(self, path, type, filename, lineno):
        if ":" in path:
            scheme, rest = urllib.splittype(path)
            if len(scheme) == 1:
                # looks like a drive letter for Windows; scream,
                # 'cause that's not allowable:
                raise InclusionSpecificationError(
                    "drive letters are not allowed in inclusions: %r"
                    % path,
                    filename, lineno)
        np = posixpath.normpath(path)
        if posixpath.isabs(np) or np[:1] == ".":
            raise InclusionSpecificationError(
                "%s path must not be absolute or refer to a location"
                " not contained in the source directory"
                % path,
                filename, lineno)
        return np.replace("/", os.sep)

    def normalizePathOrURL(self, path, type, filename, lineno):
        if ":" in path:
            scheme, rest = urllib.splittype(path)
            if len(scheme) != 1:
                # should normalize the URL, but skip that for now
                return path
        return self.normalizePath(path, type, filename, lineno)


class InclusionProcessor:
    """Handler for processing inclusion specifications.

    Methods are provided for both reading specifications and creating
    the output tree.

    """
    def __init__(self, source, destination):
        if not os.path.exists(source):
            raise InclusionError("source directory does not exist: %r"
                                 % source)
        self.source = os.path.abspath(source)
        self.destination = os.path.abspath(destination)
        self.manifests = []
        self.cvs_loader = None

    def createDistributionTree(self, spec=None):
        """Create the output tree according to the loaded specification.

        The destination directory will be created if it doesn't
        already exist.
        """
        if spec is None:
            spec = Specification(self.source)
        self.copyTree(spec.source, self.destination, spec.excludes)
        for relpath, source in spec.includes.iteritems():
            self.addSingleInclude(relpath, source)

    def copyTree(self, source, destination, excludes={}):
        """Populate the destination tree from the source tree.

        Files and directories will be created with the same permission
        bits and stat info as the source tree.

        Entries identified as exclusions will not be copied at all.
        """
        if not os.path.exists(destination):
            os.mkdir(destination)
        prefix = os.path.join(source, "")
        for dirname, dirs, files in os.walk(source):
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

            for dir in dirs:
                srcname = os.path.join(dirname, dir)
                destname = os.path.join(destdir, dir)
                # Create the directory, copying over the permission
                # bits and stat info.
                os.mkdir(destname)
                shutil.copymode(srcname, destname)
                shutil.copystat(srcname, destname)

    def copy_file(self, source, destination):
        shutil.copy2(source, destination)
        self.add_output(destination)

    def add_output(self, path):
        """Add 'path' to each of the relevant manifests."""
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
        manifest = []
        prefix = os.path.join(destination, "")
        self.manifests.append((prefix, manifest))
        return manifest

    def drop_manifest(self, destination):
        prefix = os.path.join(destination, "")
        for i in range(len(self.manifests)):
            if self.manifests[i][0] == prefix:
                del self.manifests[i]
                return
        raise ValueError("no manifest for %s" % destination)

    def addSingleInclude(self, relpath, source):
        dirname, basename = os.path.split(relpath)
        if dirname:
            destdir = os.path.join(self.destination, dirname)
            if not os.path.exists(destdir):
                os.makedirs(destdir)
        else:
            # Known to exist, so no need to create it.
            destdir = self.destination

        # This is what we want to create:
        destination = os.path.join(destdir, basename)

        try:
            cvsurl = cvsloader.parse(source)
        except ValueError:
            # not a cvs: or repository: URL
            type, rest = urllib.splittype(source)
            if type:
                # some sort of URL
                self.includeFromUrl(source, destination)
            else:
                # local path
                self.includeFromLocalTree(os.path.join(self.source, source),
                                          destination)
        else:
            if isinstance(cvsurl, cvsloader.RepositoryUrl):
                raise InclusionError("can't load from repository: URL")
            self.includeFromCvs(cvsurl, destination)

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
        if self.cvs_loader is None:
            self.cvs_loader = cvsloader.CvsLoader()
        source = self.cvs_loader.load(cvsurl.getUrl())
        self.includeFromLocalTree(source, destination)
