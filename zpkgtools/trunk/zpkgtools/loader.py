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
"""
"""

import os
import posixpath
import shutil
import tempfile
import urllib
import urllib2
import urlparse

from zpkgtools import cvsloader


def open(url, mode="r"):
    if mode[:1] != "r" or "+" in mode:
        raise ValueError("external resources must be opened in read-only mode")
    loader = Loader()
    path = loader.load(url)
    if os.path.isfile(path):
        return FileProxy(path, mode, loader, url)
    # Only files and directories come from CVS, so no need to check
    # for magical directory entries here:
    loader.cleanup()
    raise IOError(errno.EISDIR, "Is a directory", url)


class Loader:

    def __init__(self, tag=None):
        self.tag = tag or None
        self.workdirs = {}  # URL -> (directory, path, temporary)
        self.cvsloader = None

    def add_working_dir(self, url, directory, path, temporary):
        self.workdirs[url] = (directory, path, temporary)

    def cleanup(self):
        """Remove all checkouts that are present."""
        while self.workdirs:
            url, (directory, path, temporary) = self.workdirs.popitem()
            if temporary:
                if directory:
                    shutil.rmtree(directory)
                else:
                    os.unlink(path)

    def load(self, url):
        if ":" in url and url.find(":") != 1:
            type, rest = urllib.splittype(url)
            # the replace() is to support svn+ssh: URLs
            methodname = "load_" + type.replace("+", "_")
            method = getattr(self, methodname, None)
            if method is None:
                method = self.unknown_load
        else:
            method = self.file_load
        return method(url)

    def file_load(self, path):
        """Load using a local path."""
        raise NotImplementedError("is this ever used?")

    def load_file(self, url):
        # XXX This doesn't deal with file: URLs that Subversion uses,
        # where a portion of the path points to a Subversion
        # repository, and the rest points into the logical structure
        # of the repository itself.
        parts = urlparse.urlsplit(url)
        path = urllib.url2pathname(parts[2])
        if not os.path.exists(path):
            raise IOError(errno.ENOENT, "no such file or directory", path)
        self.add_working_dir(url, None, path, False)
        return path

    def load_cvs(self, url):
        if self.cvsloader is None:
            self.cvsloader = cvsloader.CvsLoader()
        parsed_url = cvsloader.parse(url)
        if not parsed_url.tag:
            parsed_url.tag = self.tag
            url = parsed_url.getUrl()
        # If we've already loaded this, use that copy.  This doesn't
        # consider fetching something with a different path that's
        # represented by a previous load():
        if url in self.workdirs:
            return self.workdirs[url][1]

        tmp = tempfile.mkdtemp(prefix="loader-")
        path = self.cvsloader.load(parsed_url, tmp)
        self.add_working_dir(url, tmp, path, True)
        return path

    def load_repository(self, url):
        raise ValueError("repository: URLs must be joined with an"
                         " appropriate revision-control base URL")

    def unknown_load(self, url):
        # XXX This could end up being called with an http: or https:
        # URL for a Subversion repository; it probably won't deal with
        # that properly.  (It definately won't if it needs to
        # integrate tag information.)
        parts = urlparse.urlparse(url)
        filename = posixpath.basename(parts[2])
        f = urllib2.urlopen(url)
        fd, tmp = tempfile.mkstemp(prefix="loader-")
        try:
            os.fwrite(fd, f.read())
        except:
            os.close(fd)
            os.unlink(tmp)
            raise
        else:
            os.close(fd)
        self.add_working_dir(url, None, tmp, True)
        return tmp


class FileProxy(object):

    def __init__(self, path, mode, loader, url=None):
        self.name = url or path
        self._file = file(path, mode)
        self._cleanup = loader.cleanup

    def __getattr__(self, name):
        return getattr(self._file, name)

    def close(self):
        if not self._file.closed:
            self._file.close()
            self._cleanup()
            self._cleanup = None

    # We shouldn't ever actually need to deal with softspace since
    # we're read-only, but... real files still behave this way, so we
    # emulate it.

    def _get_softspace(self):
        return self._file.softspace

    def _set_softspace(self, value):
        self._file.softspace = value

    softspace = property(_get_softspace, _set_softspace)
