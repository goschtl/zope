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
"""General loader support.

This handles tag insertion and URL type dispatch.
"""

import os
import posixpath
import shutil
import tempfile
import urllib
import urllib2
import urlparse

from zpkgtools import cvsloader
from zpkgtools import svnloader


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
        self.workdirs = {}  # URL -> (tmp.directory, path, istemporary)
        self.cvsloader = None
        self.svnloader = None

    def add_working_dir(self, url, directory, path, istemporary):
        self.workdirs[url] = (directory, path, istemporary)

    def cleanup(self):
        """Remove all checkouts that are present."""
        while self.workdirs:
            url, (directory, path, istemporary) = self.workdirs.popitem()
            if istemporary:
                if directory:
                    shutil.rmtree(directory)
                else:
                    os.unlink(path)

    def transform_url(self, url):
        """Transform a URL to encode the tag passed to the constructor.

        :param url:  URL that may not be associated with a particular tag.

        If `url` can be modified to encode the tag associated with the
        loader, a modified URL that does so is returned.  If not, the
        original URL is returned unmodified.
        """
        if self.tag:
            try:
                parsed_url = cvsloader.parse(url)
            except ValueError:
                pass
            else:
                if not parsed_url.tag:
                    parsed_url.tag = self.tag
                    url = parsed_url.getUrl()
        return url

    def load(self, url):
        url = self.transform_url(url)
        if url in self.workdirs:
            return self.workdirs[url][1]
        if ":" in url and url.find(":") != 1:
            type, rest = urllib.splittype(url)
            # the replace() is to support svn+ssh: URLs
            methodname = "load_" + type.replace("+", "_")
            method = getattr(self, methodname, None)
            if method is None:
                method = self.unknown_load
        else:
            raise ValueError("can only load from URLs, not path references")
        path = method(url)
        assert path == self.workdirs[url][1]
        return path

    def load_mutable_copy(self, url):
        """Load the resource referenced by `url` so the application
        can modify it.

        If the copy provided by the `load()` method isn't 'owned' by
        the application (because it's a temporary copy), a copy will
        be made and used instead.
        """
        url = self.transform_url(url)
        self.load(url)
        directory, path, istemporary = self.workdirs[url]
        if not istemporary:
            # We need a copy we can mutate and throw away later:
            p = self.create_copy(url, path)
            assert p != path
            path = p
        assert path == self.workdirs[url][1]
        assert self.workdirs[url][2]
        return path

    def create_copy(self, url, path):
        """Create a copy of the tree rooted at `path`.

        The copy must be 'owned' by the application, and can be
        mutated freely without affecting the original.
        """
        tmpdir = tempfile.mkdtemp(prefix="loader-")
        # we have to normalize in case there's a trailing slash
        path = os.path.normpath(path)
        basename = os.path.basename(path)
        filename = os.path.join(tmpdir, basename)
        if os.path.isfile(path):
            shutil.copy2(path, filename)
        else:
            shutil.copytree(path, filename, symlinks=False)
        self.add_working_dir(url, tmpdir, filename, True)
        return filename

    def load_file(self, url):
        if svnloader.is_subversion_url(url):
            return self.load_svn(url)
        parts = urlparse.urlsplit(url)
        path = urllib.url2pathname(parts[2])
        if not os.path.exists(path):
            raise IOError(errno.ENOENT, "no such file or directory", path)
        self.add_working_dir(url, None, path, False)
        return path

    def load_cvs(self, url):
        if self.cvsloader is None:
            self.cvsloader = cvsloader.CvsLoader()
        tmp = tempfile.mkdtemp(prefix="cvsloader-")
        parsed_url = cvsloader.parse(url)
        path = self.cvsloader.load(parsed_url, tmp)
        self.add_working_dir(url, tmp, path, True)
        return path

    def load_repository(self, url):
        raise ValueError("repository: URLs must be joined with an"
                         " appropriate revision-control base URL")

    def load_svn(self, url):
        if self.svnloader is None:
            self.svnloader = svnloader.SubversionLoader()
        tmp = tempfile.mkdtemp(prefix="svnloader-")
        path = self.svnloader.load(url, tmp)
        self.add_working_dir(url, tmp, path, True)
        return path

    def load_svn_ssh(self, url):
        return self.load_svn(url)

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
            os.write(fd, f.read())
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
