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

$Id: fssync.py,v 1.3 2003/05/11 00:23:23 gvanrossum Exp $
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
from zope.fssync.compare import treeComparisonWalker

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
        self.merge(self.topdir, tmpdir)
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
                self.merge(self.topdir, tmpdir)
                print "All done"
            finally:
                shutil.rmtree(tmpdir)
        finally:
            os.unlink(filename)

    def add(self, path):
        path = realpath(path)
        if not exists(path):
            raise Error("nothing known about '%s'", path)
        dir, name = split(path)
        if name in ("", os.curdir, os.pardir):
            raise Error("can't add path '%s'", path)
        entries = self.loadentries(dir)
        if name in entries:
            raise Error("path '%s' is already registered", name)
        pdir = self.parent(dir)
        dname = basename(dir)
        pentries = self.loadentries(pdir)
        if dname not in pentries:
            raise Error("directory '%s' unknown", dname)
        dpath = pentries[dname]['path']
        if dpath == "/":
            ourpath = "/" + name
        else:
            ourpath = dpath + "/" + name
        entries[name] = d = {"path": ourpath, "flag": "added"}
        if isdir(path):
            d["type"] = "zope.app.content.folder.Folder"
            self.ensuredir(join(path, "@@Zope"))
            self.dumpentries({}, path)
        else:
            # XXX Need to guess better based on extension
            d["type"] = "zope.app.content.file.File"
        if "factory" not in d:
            d["factory"] = str(unicode(d["type"]))
        self.dumpentries(entries, dir)

    def merge(self, ours, server):
        # XXX This method is way too long, and still not complete :-(
        for (left, right, common, lentries, rentries, ldirs, lnondirs,
             rdirs, rnondirs) in treeComparisonWalker(ours, server):
            origdir = join(left, "@@Zope", "Original")
            lextradir = join(left, "@@Zope", "Extra")
            rextradir = join(right, "@@Zope", "Extra")
            lanndir = join(left, "@@Zope", "Annotations")
            ranndir = join(right, "@@Zope", "Annotations")
            weirdos = ldirs.copy() # This is for flagging "?" files
            weirdos.update(lnondirs)
            for x in common: # Compare matching stuff
                nx = normpath(x)
                if nx in weirdos:
                    del weirdos[nx]
                if nx in rdirs:
                    if nx in lnondirs:
                        print "file '%s' is in the way of a directory"
                    elif nx not in ldirs:
                        print "restoring directory '%s'"
                        os.mkdir(join(left, x))
                elif nx in rnondirs:
                    if nx in ldirs:
                        print "directory '%s' is in the way of a file"
                    else:
                        # Merge files
                        rx = rnondirs[nx]
                        origx = join(origdir, x)
                        if nx in lnondirs:
                            lx = lnondirs[nx]
                        else:
                            lx = join(left, x)
                            print "restoring lost file '%s'" % lx
                            self.copyfile(origx, lx)
                        if self.cmp(origx, rx):
                            # Unchanged on server
                            if self.cmp(lx, origx):
                                if self.verbose:
                                    print "=", lx
                            else:
                                print "M", lx
                        elif self.cmp(lx, origx):
                            # Unchanged locally
                            self.copyfile(rx, lx)
                            self.copyfile(rx, origx)
                            print "U", lx
                        elif self.cmp(lx, rx):
                            # Only the original is out of date
                            self.copyfile(rx, origx)
                            print "U", lx
                        else:
                            # Conflict!  Must do a 3-way merge
                            print "merging changes into '%s'" % lx
                            self.copyfile(rx, origx)
                            sts = os.system("merge %s %s %s" %
                                            (commands.mkarg(lx),
                                             commands.mkarg(origx),
                                             commands.mkarg(rx)))
                            if sts:
                                print "C", lx
                            else:
                                print "M", lx
                # In all cases, merge Extra stuff if any
                lx = join(lextradir, x)
                rx = join(rextradir, x)
                if isdir(rx):
                    self.ensuredir(lx)
                    self.merge(lx, rx)
                # And merge Annotations if any
                lx = join(lanndir, x)
                rx = join(ranndir, x)
                if isdir(rx):
                    self.ensuredir(lx)
                    self.merge(lx, rx)
            entries = self.loadentries(left)
            entries_changed = False
            for x in rentries: # Copy new stuff from server
                entries[x] = rentries[x]
                entries_changed = True
                nx = normpath(x)
                if nx in rdirs:
                    del weirdos[nx]
                    # New directory; traverse into it
                    if nx in lnondirs:
                        print ("file '%s' is in the way of a new directory" %
                               lnondirs[nx])
                    else:
                        common[x] = ({}, rentries[x])
                        del rentries[x]
                        if nx not in ldirs:
                            lfull = join(left, x)
                            os.mkdir(lx)
                            ldirs[nx] = lx
                elif nx in rnondirs:
                    if nx in ldirs:
                        print ("directory '%s' is in the way of a new file" %
                               ldirs[nx])
                    elif nx in lnondirs:
                        if self.cmp(rnondirs[nx], lnondirs[nx]):
                            print "U", lnondirs[nx]
                            del weirdos[nx]
                        else:
                            print ("file '%s' is in the way of a new file" %
                                   lnondirs[nx])
                    else:
                        # New file; copy it
                        lx = join(left, x)
                        rx = join(right, x)
                        self.copyfile(rx, lx)
                        # And copy to Original
                        self.ensuredir(origdir)
                        self.copyfile(rx, join(origdir, x))
                        print "U", lx
                # In all cases, copy Extra stuff if any
                lx = join(lextradir, x)
                rx = join(rextradir, x)
                if isdir(rx):
                    self.ensuredir(lx)
                    self.merge(lx, rx)
                # And copy Annotations if any
                lx = join(lanndir, x)
                rx = join(ranndir, x)
                if isdir(rx):
                    self.ensuredir(lx)
                    self.merge(lx, rx)
            if entries_changed:
                self.dumpentries(entries, left)
            for x in lentries: # Flag new stuff in the working directory
                # XXX Could be deleted on server too!!!
                nx = normpath(x)
                if nx in weirdos:
                    print "A", weirdos[nx]
                    del weirdos[nx]
                else:
                    lx = join(left, x)
                    print "newborn '%s' is missing" % lx
                # XXX How about Annotations and Extra for these?
            # Flag anything not yet noted
            for nx in weirdos:
                if not self.ignore(nx):
                    print "?", weirdos[nx]

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

    def loadentries(self, dir):
        file = join(dir, "@@Zope", "Entries.xml")
        try:
            return self.loadfile(file)
        except IOError:
            return {}

    def dumpentries(self, entries, dir):
        file = join(dir, "@@Zope", "Entries.xml")
        self.dumpfile(entries, file)

    def loadfile(self, file):
        data = self.readfile(file)
        return loads(data)

    def dumpfile(self, obj, file):
        data = dumps(obj)
        self.writefile(data, file)

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
