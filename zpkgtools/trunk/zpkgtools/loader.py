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

import errno
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
    """Return a file-like object representing the resource at `url`.

    :return: A `FileProxy` instance representing the resource.

    :param url: The URL for the resource.

    :param mode: The mode in which the resource should be opened; the
      mode must indicate read-only access.

    :raises ValueError: If `mode` indicates anything other than
      read-only.

    :raises IOError: If `url` refers to a directory resource.  The
      ``errno`` member will be `errno.EISDIR`, and the ``filename``
      field will be `url`.

    The resource must be a file; it cannot be a directory.
    """
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
    """General-purpose resource loader.


    """

    def __init__(self, tag=None):
        """Initialize the loader.

        :param tag: The revision tag that should be used for resources
          under revision control.
        """
        self.tag = tag or None
        self.workdirs = {}  # URL -> (tmp.directory, path, istemporary)
        self.cvsloader = None
        self.svnloader = None

    def add_working_dir(self, url, directory, path, istemporary):
        """Add a cache entry for `url`.

        :param directory: A directory which serves as a container for
          the resource.  If the copy is temporary, this is the
          directory which should be deleted.

        :param path: The path of the copy of the resource.  If
          `directory` is not ``None``, this path will be inside the
          hierarchy rooted at `directory`.

        :param istemporary: Boolean flag indicating whether this entry
          references a temporary copy (which is therefore mutable) or
          a non-temporary copy.
        """
        self.workdirs[url] = (directory, path, istemporary)

    def cleanup(self):
        """Remove all temporary copies created by the loader."""
        while self.workdirs:
            url, (directory, path, istemporary) = self.workdirs.popitem()
            if istemporary:
                if directory:
                    shutil.rmtree(directory)
                else:
                    os.unlink(path)

    def transform_url(self, url):
        """Transform a URL to encode the tag passed to the constructor.

        :param url:  URL that might not be associated with a particular tag.

        :return: The transformed URL.

        If `url` can be modified to encode the tag associated with the
        loader, a modified URL that does so is returned.  If not, the
        original URL is returned unmodified.
        """
        if self.tag:
            try:
                parsed_url = cvsloader.parse(url)
            except ValueError:
                try:
                    parsed_url = svnloader.parse(url)
                except ValueError:
                    pass
                else:
                    if not parsed_url.tag:
                        parsed_url.tag = self.tag
                        url = parsed_url.getUrl()
            else:
                if not parsed_url.tag:
                    parsed_url.tag = self.tag
                    url = parsed_url.getUrl()
        return url

    def load(self, url):
        """Load the resource referenced by `url`.

        :param url: URL of the resource to load.

        :return: A local filesystem path containing the resource.

        If the resource has already been loaded, that copy will be
        used again.
        """
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

        :param url: URL of the resource to load.

        :return: A local filesystem path containing a mutable copy of
          the resource.

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

        :param url: URL of the resource that's being copied.

        :param path: Local filesystem path containing an immutable
          copy of the resource loaded from `url`.

        :return: A local filesystem path containing a mutable copy of
          the resource.

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
        """Load a URL type that isn't handled specially.

        :param url: URL of the resource to load.

        :return: Local filesystem path containing the resource.

        This method simply dispatches to the `urllib2.urlopen()`
        function, so it's not able to load directory resources.
        """
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
    """Proxy object for a file handled by a private loader.

    When this file object is closed, the loader is cleaned up as well,
    removing any temporary copies from the filesystem.
    """

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

    softspace = property(_get_softspace, _set_softspace,
                         doc="Boolean that indicates whether a space"
                         " character needs to be printed before another"
                         " value when using the ``print`` statement.")
