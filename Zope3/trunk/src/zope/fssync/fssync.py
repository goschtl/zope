##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Support classes for fssync.

$Id: fssync.py,v 1.4 2003/05/12 20:19:38 gvanrossum Exp $
"""

import os
import base64
import shutil
import urllib
import filecmp
import htmllib
import httplib
import commands
import tempfile
import urlparse
import formatter

from StringIO import StringIO

from os.path import exists, isfile, isdir, islink
from os.path import dirname, basename, split, join
from os.path import realpath, normcase, normpath

from zope.xmlpickle import loads, dumps
from zope.fssync.compare import treeComparisonWalker, classifyContents
from zope.fssync.metadata import Metadata
from zope.fssync.merger import Merger

class Error(Exception):
    """User-level error, e.g. non-existent file.

    This can be used in several ways:

        1) raise Error("message")
        2) raise Error("message %r %r" % (arg1, arg2))
        3) raise Error("message %r %r", arg1, arg2)
        4) raise Error("message", arg1, arg2)

    - Forms 2-4 are equivalent.

    - Form 4 assumes that "message" contains no % characters.

    - When using forms 2 and 3, all % formats are supported.

    - Form 2 has the disadvantage that when you specify a single
      argument that happens to be a tuple, it may get misinterpreted.

    - The message argument is required.

    - Any number of arguments after that is allowed.
    """

    def __init__(self, msg, *args):
        self.msg = msg
        self.args = args

    def __str__(self):
        msg, args = self.msg, self.args
        if args:
            if "%" in msg:
                msg = msg % args
            else:
                msg += " ".join(map(repr, args))
        return str(msg)

    def __repr__(self):
        return "%s%r" % (self.__class__.__name__, (self.msg,)+self.args)

class FSSync(object):

    def __init__(self, topdir, verbose=False):
        self.topdir = topdir
        self.verbose = verbose
        self.rooturl = self.findrooturl()
        self.metadata = Metadata()

    def setrooturl(self, rooturl):
        self.rooturl = rooturl

    def checkout(self):
        fspath = self.topdir
        if not self.rooturl:
            raise Error("root url not found nor explicitly set")
        if os.path.exists(fspath):
            raise Error("can't checkout into existing directory", fspath)
        url = self.rooturl
        if not url.endswith("/"):
            url += "/"
        url += "@@toFS.zip?writeOriginals=True"
        filename, headers = urllib.urlretrieve(url)
        if headers["Content-Type"] != "application/zip":
            raise Error("The request didn't return a zipfile; contents:\n%s",
                        self.slurptext(self.readfile(filename),
                                       headers).strip())
        try:
            os.mkdir(fspath)
            sts = os.system("cd %s; unzip -q %s" % (fspath, filename))
            if sts:
                raise Error("unzip command failed")
            self.saverooturl()
            print "All done"
        finally:
            os.unlink(filename)

    def commit(self):
        fspath = self.topdir
        if not self.rooturl:
            raise Error("root url not found")
        (scheme, netloc, url, params,
         query, fragment) = urlparse.urlparse(self.rooturl)
        if scheme != "http":
            raise Error("root url must start with http", rooturl)
        user_passwd, host_port = urllib.splituser(netloc)
        zipfile = tempfile.mktemp(".zip")
        sts = os.system("cd %s; zip -q -r %s ." % (fspath, zipfile))
        if sts:
            raise Error("zip command failed")
        zipdata = self.readfile(zipfile, "rb")
        os.unlink(zipfile)
        # XXX Use urllib2 and then set Content-type header.
        # That should take care of proxies and https.
        h = httplib.HTTP(host_port)
        h.putrequest("POST", url + "/@@fromFS.zip")
        h.putheader("Content-Type", "application/zip")
        h.putheader("Content-Length", str(len(zipdata)))
        if user_passwd:
            auth = base64.encodestring(user_passwd).strip()
            h.putheader('Authorization', 'Basic %s' % auth)
        h.putheader("Host", host_port)
        h.endheaders()
        h.send(zipdata)
        errcode, errmsg, headers = h.getreply()
        if errcode != 200:
            raise Error("HTTP error %s (%s); error document:\n%s",
                        errcode, errmsg,
                        self.slurptext(h.getfile().read(), headers))
        if headers["Content-Type"] != "application/zip":
            raise Error("The request didn't return a zipfile; contents:\n%s",
                        self.slurptext(h.getfile().read(), headers))
        f = open(zipfile, "wb")
        shutil.copyfileobj(h.getfile(), f)
        f.close()
        tmpdir = tempfile.mktemp()
        os.mkdir(tmpdir)
        sts = os.system("cd %s; unzip -q %s" % (tmpdir, zipfile))
        if sts:
            raise Error("unzip command failed")
        self.merge_dirs(self.topdir, tmpdir)
        shutil.rmtree(tmpdir)
        os.unlink(zipfile)
        print "All done"

    def update(self):
        url = self.rooturl
        if not url.endswith("/"):
            url += "/"
        url += "@@toFS.zip?writeOriginals=False"
        filename, headers = urllib.urlretrieve(url)
        try:
            if headers["Content-Type"] != "application/zip":
                raise Error("The request didn't return a zipfile; "
                            "contents:\n%s",
                            self.slurptext(self.readfile(filename),
                                           headers).strip())
            tmpdir = tempfile.mktemp()
            os.mkdir(tmpdir)
            try:
                sts = os.system("cd %s; unzip -q %s" % (tmpdir, filename))
                if sts:
                    raise Error("unzip command failed")
                self.merge_dirs(self.topdir, tmpdir)
                print "All done"
            finally:
                shutil.rmtree(tmpdir)
        finally:
            os.unlink(filename)

    def add(self, path):
        if not exists(path):
            raise Error("nothing known about '%s'", path)
        entry = self.metadata.getentry(path)
        if entry:
            raise Error("path '%s' is already registered", name)
        entry["path"] = '/'+path
        entry["flag"] = "added"
        if isdir(path):
            entry["type"] = "zope.app.content.folder.Folder"
            self.ensuredir(join(path, "@@Zope"))
            self.dumpentries({}, path)
        else:
            # XXX Need to guess better based on extension
            entry["type"] = "zope.app.content.file.File"
        if "factory" not in entry:
            entry["factory"] = str(unicode(entry["type"]))
        self.metadata.flush()

    def merge_dirs(self, localdir, remotedir):
        merger = Merger(self.metadata)

        ldirs, lnondirs = classifyContents(localdir)
        rdirs, rnondirs = classifyContents(remotedir)

        dirs = {}
        dirs.update(ldirs)
        dirs.update(rdirs)

        nondirs = {}
        nondirs.update(lnondirs)
        nondirs.update(rnondirs)

        def sorted(d): keys = d.keys(); keys.sort(); return keys

        for x in sorted(dirs):
            local = join(localdir, x)
            if x in nondirs:
                # Too weird to handle
                print "should '%s' be a directory or a file???" % local
                continue
            remote = join(remotedir, x)
            lentry = self.metadata.getentry(local)
            rentry = self.metadata.getentry(remote)
            if lentry or rentry:
                if x not in ldirs:
                    os.mkdir(local)
            self.merge_dirs(local, remote)

        for x in sorted(nondirs):
            if x in dirs:
                # Error message was already printed by previous loop
                continue
            local = join(localdir, x)
            origdir = join(localdir, "@@Zope", "Original")
            self.ensuredir(origdir)
            orig = join(origdir, x)
            remote = join(remotedir, x)
            action, state = merger.classify_files(local, orig, remote)
            state = merger.merge_files(local, orig, remote, action, state)
            self.report(action, state, local)
            self.merge_extra(local, remote)
            self.merge_annotations(local, remote)

        self.merge_extra(localdir, remotedir)
        self.merge_annotations(localdir, remotedir)

        self.metadata.flush()

    def merge_extra(self, local, remote):
        lhead, ltail = split(local)
        rhead, rtail = split(remote)
        lextra = join(lhead, "@@Zope", "Extra", ltail)
        rextra = join(rhead, "@@Zope", "Extra", rtail)
        if isdir(rextra):
            self.ensuredir(lextra)
            self.merge_dirs(lextra, rextra)

    def merge_annotations(self, local, remote):
        lhead, ltail = split(local)
        rhead, rtail = split(remote)
        lannotations = join(lhead, "@@Zope", "Annotations", ltail)
        rannotations = join(rhead, "@@Zope", "Annotations", rtail)
        if isdir(rannotations):
            self.ensuredir(lannotations)
            self.merge_dirs(lannotations, rannotations)

    def report(self, action, state, local):
        if action != "Nothing":
            print action, local
        letter = None
        if state == "Conflict":
            letter = "C"
        elif state == "Uptodate":
            if action in ("Copy", "Fix", "Merge"):
                letter = "U"
        elif state == "Modified":
            letter = "M"
        elif state == "Added":
            letter = "A"
        elif state == "Removed":
            letter = "R"
        elif state == "Spurious":
            if not self.ignore(local):
                letter = "?"
        elif state == "Nonexistent":
            if action == "Delete":
                print "local file '%s' is no longer relevant" % local
        if letter:
            print letter, local

    def ignore(self, path):
        return path.endswith("~")

    def cmp(self, f1, f2):
        try:
            return filecmp.cmp(f1, f2, shallow=False)
        except (os.error, IOError):
            return False

    def copyfile(self, src, dst):
        shutil.copyfile(src, dst)

    def ensuredir(self, dir):
        if not isdir(dir):
            os.makedirs(dir)

    def slurptext(self, data, headers):
        ctype = headers["content-type"]
        if ctype == "text/html":
            s = StringIO()
            f = formatter.AbstractFormatter(formatter.DumbWriter(s))
            p = htmllib.HTMLParser(f)
            p.feed(data)
            p.close()
            return s.getvalue()
        if ctype.startswith("text/"):
            return data
        return "Content-Type %r" % ctype

    def findrooturl(self):
        dir = self.topdir
        while dir:
            zopedir = join(dir, "@@Zope")
            rootfile = join(zopedir, "Root")
            try:
                data = self.readfile(rootfile)
                return data.strip()
            except IOError:
                pass
            dir = self.parent(dir)
        return None

    def saverooturl(self):
        if self.rooturl:
            self.writefile(self.rooturl + "\n",
                           join(self.topdir, "@@Zope", "Root"))

    def readfile(self, file, mode="r"):
        f = open(file, mode)
        try:
            return f.read()
        finally:
            f.close()

    def writefile(self, data, file, mode="w"):
        f = open(file, mode)
        try:
            f.write(data)
        finally:
            f.close()

    def parent(self, path):
        anomalies = ("", os.curdir, os.pardir)
        head, tail = split(path)
        if tail not in anomalies:
            return head
        head, tail = split(normpath(path))
        if tail not in anomalies:
            return head
        head, tail = split(realpath(path))
        if tail not in anomalies:
            return head
        return None
