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

import glob
import os
import posixpath
import shutil
import urllib
import urllib2

from zpkgtools import cvsloader


# Names that are exluded from globbing results:
EXCLUDE_NAMES = ["CVS", ".cvsignore", "RCS", "SCCS", ".svn"]


class InclusionError(Exception):
    pass


class InclusionSpecificationError(ValueError, InclusionError):
    def __init__(self, message, filename, lineno):
        self.filename = filename
        self.lineno = lineno
        ValueError.__init__(self, message)


class InclusionProcessor:
    """Handler for processing inclusion specifications.

    Methods are provided for both reading specifications and creating
    the output tree.

    The following attributes are filled in by loadSpecification().
    These are exposed for use from the unit tests.

    excludes
      Iterable containing the absolute path names of the files in the
      source tree that should not be part of the destination.

    includes
      Mapping from relative path (relative to the destination) to
      either an absolute path in the source directory or a URL.

    """
    def __init__(self, source, destination, specfile=None):
        if not os.path.exists(source):
            raise InclusionError("source directory does not exist: %r"
                                 % source)
        self.source = os.path.abspath(source)
        self.destination = os.path.abspath(destination)
        prefix = os.path.commonprefix([self.source, self.destination])
        if prefix == self.source:
            raise InclusionError("destination directory may not be"
                                 " contained in the source directory")
        elif prefix == self.destination:
            raise InclusionError("source directory may not be"
                                 " contained in the destination directory")
        self.excludes = {}
        self.includes = {}
        f = None
        if specfile is None:
            # Read soruce/INCLUDES.txt, if it exists.
            specfile = os.path.join(source, "INCLUDES.txt")
            if os.path.exists(specfile):
                f = open(specfile, "rU")
            contextdir = self.source
        else:
            # Read the specified file, without testing for existance.
            f = open(specfile, "rU")
            contextdir = os.path.dirname(os.path.abspath(specfile))
        if f is not None:
            try:
                self.loadSpecification(f, specfile)
            finally:
                f.close()
        if os.path.isdir(os.path.join(contextdir, "CVS")):
            self.cvsurl = cvsloader.fromPath(contextdir)
        else:
            self.cvsurl = None
        self.cvs_loader = None

    def loadSpecification(self, f, filename):
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
                expansions = self.glob(path)
                if not expansions:
                    raise InclusionSpecificationError(
                        "exclusion %r doesn't match any files" % dest,
                        filename, lineno)
                for fn in expansions:
                    self.excludes[fn] = fn
            else:
                self.includes[dest] = src

    def glob(self, pattern):
        return [n for n in glob.glob(pattern)
                if os.path.basename(n) not in EXCLUDE_NAMES]

    def filterNames(self, names):
        return [n for n in names
                if n not in EXCLUDE_NAMES]

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

    def createDistributionTree(self):
        """Create the output tree according to the loaded specification.

        The destination directory will be created if it doesn't
        already exist.
        """
        self.copyTree(self.source, self.destination)
        self.addIncludes()

    def copyTree(self, source, destination):
        """Populate the destination tree from the source tree.

        Files and directories will be created with the same permission
        bits and stat info as the source tree.

        Entries identified as exclusions will not be copied at all.
        """
        if not os.path.exists(destination):
            os.mkdir(destination)
        prefix = os.path.join(source, "")
        for dirname, dirs, files in os.walk(source):
            dirs[:] = self.filterNames(dirs)
            files = self.filterNames(files)

            # remove excluded directories:
            for dir in dirs[:]:
                fullpath = os.path.join(dirname, dir)
                if fullpath in self.excludes:
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
                if srcname in self.excludes:
                    continue
                destname = os.path.join(destdir, file)
                # Copy file data, permission bits, and stat info;
                # owner/group are not copied.
                shutil.copy2(srcname, destname)

            for dir in dirs:
                srcname = os.path.join(dirname, dir)
                destname = os.path.join(destdir, dir)
                # Create the directory, copying over the permission
                # bits and stat info.
                os.mkdir(destname)
                shutil.copymode(srcname, destname)
                shutil.copystat(srcname, destname)

    def addIncludes(self):
        """Add files and directories based on the specification."""
        for relpath, source in self.includes.iteritems():
            self.addSingleInclude(relpath, source)

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
            self.includeFromCvs(cvsurl, destination)

    def includeFromLocalTree(self, source, destination):
        # Check for file-ness here since copyTree() doesn't handle
        # individual files at all.
        if os.path.isfile(source):
            shutil.copy2(source, destination)
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
        finally:
            inf.close()

    def includeFromCvs(self, cvsurl, destination):
        loader = self.getLoader(cvsurl)
        source = loader.load(cvsurl)
        if os.path.isfile(source):
            shutil.copy2(source, destination)
        else:
            self.copyTree(source, destination)

    def getLoader(self, cvsurl):
        if self.cvs_loader is None and self.cvsurl is not None:
            self.cvs_loader = cvsloader.CvsLoader(self.cvsurl)
        if self.cvs_loader is None:
            # We can create a temporary loader from a cvs: URL if we need to:
            if isinstance(cvsurl, cvsloader.CvsUrl):
                loader = cvsloader.CvsLoader(cvsurl)
            else:
                # We don't have a cvs: URL, and repository: URLs are
                # always relative to a cvs: URL, so we can't proceed:
                raise InclusionError(
                    "cannot load URL %s without base repository information"
                    % cvsurl.getUrl())
        else:
            loader = self.cvs_loader
        return loader
