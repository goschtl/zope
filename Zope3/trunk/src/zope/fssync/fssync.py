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

$Id: fssync.py,v 1.5 2003/05/12 22:23:42 gvanrossum Exp $
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
        self.setrooturl(self.findrooturl())
        self.metadata = Metadata()

    def setrooturl(self, rooturl):
        self.rooturl = rooturl
        if self.rooturl is None:
            self.roottype = self.rootpath = None
            self.user_passwd = self.host_port = None
            return
        self.roottype, rest = urllib.splittype(self.rooturl)
        if self.roottype not in ("http", "https"):
            raise Error("root url must be 'http' or 'https'", self.rooturl)
        if self.roottype == "https" and not hasattr(httplib, "HTTPS"):
            raise Error("https not supported by this Python build")
        netloc, self.rootpath = urllib.splithost(rest)
        self.user_passwd, self.host_port = urllib.splituser(netloc)

    def httpreq(self, path, view, datafp=None, content_type="application/zip"):
        if not path.endswith("/"):
            path += "/"
        path += view
        if self.roottype == "https":
            h = httplib.HTTPS(self.host_port)
        else:
            h = httplib.HTTP(self.host_port)
        if datafp is None:
            h.putrequest("GET", path)
            filesize = 0   # for PyChecker
        else:
            datafp.seek(0, 2)
            filesize = datafp.tell()
            datafp.seek(0)
            h.putrequest("POST", path)
            h.putheader("Content-type", content_type)
            h.putheader("Content-length", str(filesize))
        if self.user_passwd:
            auth = base64.encodestring(self.user_passwd).strip()
            h.putheader('Authorization', 'Basic %s' % auth)
        h.putheader("Host", self.host_port)
        h.endheaders()
        if datafp is not None:
            nbytes = 0
            while True:
                buf = datafp.read(8192)
                if not buf:
                    break
                nbytes += len(buf)
                h.send(buf)
            assert nbytes == filesize
        errcode, errmsg, headers = h.getreply()
        fp = h.getfile()
        if errcode != 200:
            raise Error("HTTP error %s (%s); error document:\n%s",
                        errcode, errmsg,
                        self.slurptext(fp, headers))
        if headers["Content-type"] != "application/zip":
            raise Error("The request didn't return a zipfile:\n%s",
                        self.slurptext(fp, headers).strip())
        return fp, headers

    def checkout(self):
        fspath = self.topdir
        if not self.rooturl:
            raise Error("root url not found nor explicitly set")
        if os.path.exists(fspath):
            raise Error("can't checkout into existing directory", fspath)
        fp, headers = self.httpreq(self.rootpath,
                                   "@@toFS.zip?writeOriginals=False")
        try:
            self.merge_zipfile(fp)
        finally:
            fp.close()
        self.saverooturl()

    def commit(self):
        names = self.metadata.getnames(self.topdir)
        if len(names) != 1:
            raise Error("can only commit from toplevel directory")
        entry = self.metadata.getentry(join(self.topdir, names[0]))
        path = entry["path"]
        zipfile = tempfile.mktemp(".zip")
        try:
            sts = os.system("cd %s; zip -q -r %s ." %
                            (commands.mkarg(self.topdir), zipfile))
            if sts:
                raise Error("zip command failed")
            infp = open(zipfile, "rb")
            try:
                outfp, headers = self.httpreq(path, "@@fromFS.zip", infp)
            finally:
                infp.close()
        finally:
            pass
            if isfile(zipfile):
                os.remove(zipfile)
        try:
            self.merge_zipfile(outfp)
        finally:
            outfp.close()

    def update(self):
        fp, headers = self.httpreq(self.rootpath,
                                   "@@toFS.zip?writeOriginals=False")
        try:
            if headers["Content-Type"] != "application/zip":
                raise Error("The request didn't return a zipfile:\n%s",
                            self.slurptext(fp, headers).strip())
            self.merge_zipfile(fp)
        finally:
            fp.close()

    def merge_zipfile(self, fp):
        zipfile = tempfile.mktemp(".zip")
        try:
            tfp = open(zipfile, "wb")
            try:
                shutil.copyfileobj(fp, tfp)
            finally:
                tfp.close()
            tmpdir = tempfile.mktemp()
            try:
                os.mkdir(tmpdir)
                cmd = "cd %s; unzip -q %s" % (tmpdir, zipfile)
                sts, output = commands.getstatusoutput(cmd)
                self.merge_dirs(self.topdir, tmpdir)
                print "All done."
            finally:
                if isdir(tmpdir):
                    shutil.rmtree(tmpdir)
        finally:
            if isfile(zipfile):
                os.remove(zipfile)

    def add(self, path):
        if not exists(path):
            raise Error("nothing known about '%s'", path)
        entry = self.metadata.getentry(path)
        if entry:
            raise Error("path '%s' is already registered", path)
        head, tail = split(path)
        unwanted = ("", os.curdir, os.pardir)
        if tail in unwanted:
            path = realpath(path)
            head, tail = split(path)
            if head == path or tail in unwanted:
                raise Error("can't add '%s': it is the system root directory")
        pentry = self.metadata.getentry(head)
        if not pentry:
            raise Error("can't add '%s': its parent is not registered", path)
        if "path" not in pentry:
            raise Error("can't add '%s': its parent has no 'path' key", path)
        zpath = pentry["path"]
        if not zpath.endswith("/"):
            zpath += "/"
        zpath += tail
        entry["path"] = zpath
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
        self.ensuredir(localdir)

        ldirs, lnondirs = classifyContents(localdir)
        rdirs, rnondirs = classifyContents(remotedir)

        dirs = {}
        dirs.update(ldirs)
        dirs.update(rdirs)

        nondirs = {}
        nondirs.update(lnondirs)
        nondirs.update(rnondirs)

        def sorted(d): keys = d.keys(); keys.sort(); return keys

        merger = Merger(self.metadata)

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

        lentry = self.metadata.getentry(localdir)
        rentry = self.metadata.getentry(remotedir)
        lentry.update(rentry)

        self.metadata.flush()

    def merge_extra(self, local, remote):
        lhead, ltail = split(local)
        rhead, rtail = split(remote)
        lextra = join(lhead, "@@Zope", "Extra", ltail)
        rextra = join(rhead, "@@Zope", "Extra", rtail)
        if isdir(rextra):
            self.merge_dirs(lextra, rextra)

    def merge_annotations(self, local, remote):
        lhead, ltail = split(local)
        rhead, rtail = split(remote)
        lannotations = join(lhead, "@@Zope", "Annotations", ltail)
        rannotations = join(rhead, "@@Zope", "Annotations", rtail)
        if isdir(rannotations):
            self.merge_dirs(lannotations, rannotations)

    def report(self, action, state, local):
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
        # XXX This should have a larger set of default patterns to
        # ignore, and honor .cvsignore
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

    def slurptext(self, fp, headers):
        data = fp.read()
        ctype = headers["Content-type"]
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
        else:
            print "No root url saved"

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
