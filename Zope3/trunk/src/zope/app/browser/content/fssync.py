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

"""Code for the toFS.snarf view and its inverse, fromFS.snarf.

$Id: fssync.py,v 1.18 2003/06/05 16:38:37 gvanrossum Exp $
"""

import os
import cgi
import shutil
import tempfile

from transaction import get_transaction

from zope.publisher.browser import BrowserView
from zope.app.traversing import objectName, getParent, getRoot
from zope.app.interfaces.exceptions import UserError
from zope.fssync.snarf import Snarfer, Unsnarfer
from zope.app.fssync.syncer import toFS
from zope.app.fssync.committer import Committer, Checker
from zope.fssync.metadata import Metadata

def snarf_dir(response, dirname):
    """Helper to snarf a directory to the response."""
    response.setStatus(200)
    response.setHeader("Content-Type", "application/x-snarf")
    snf = Snarfer(response)
    snf.addtree(dirname)
    return ""

class SnarfFile(BrowserView):

    """View returning a snarfed representation of an object tree.

    This applies to any object (for="zope.interface.Interface").
    """

    def show(self):
        """Return the snarfed response."""
        dirname = tempfile.mktemp()
        try:
            os.mkdir(dirname)
            toFS(self.context, objectName(self.context) or "root", dirname)
            return snarf_dir(self.request.response, dirname)
        finally:
            if os.path.isdir(dirname):
                shutil.rmtree(dirname)

class SnarfCommit(BrowserView):

    """View for committing changes.

    This should be a POST request whose data is a snarf archive;
    it returns an updated snarf archive, or a text document with errors.
    """

    def commit(self):
        self.check_content_type()
        self.get_transaction()
        self.set_note()
        try:
            self.make_tempdir()
            self.unsnarf_body()
            self.set_arguments()
            self.make_metadata()
            self.call_checker()
            if self.errors:
                return self.send_errors()
            else:
                self.call_committer()
                self.write_to_filesystem()
                return self.send_archive()
        finally:
            self.remove_tempdir()

    def check_content_type(self):
        if not self.request.getHeader("Content-Type") == "application/x-snarf":
            raise ValueError("Content-Type is not application/x-snarf")

    def get_transaction(self):
        self.txn = get_transaction()

    def set_note(self):
        note = self.request.get("note")
        if not note:
            # XXX Hack because cgi doesn't parse the query string
            qs = self.request._environ.get("QUERY_STRING")
            if qs:
                d = cgi.parse_qs(qs)
                notes = d.get("note")
                if notes:
                    note = " ".join(notes)
        if note:
            self.txn.note(note)

    tempdir = None

    def make_tempdir(self):
        self.tempdir = tempfile.mktemp()
        os.mkdir(self.tempdir)

    def remove_tempdir(self):
        if self.tempdir and os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def unsnarf_body(self):
        fp = self.request.bodyFile
        fp.seek(0)
        uns = Unsnarfer(fp)
        uns.unsnarf(self.tempdir)

    def set_arguments(self):
        # Set self.{name, container, fspath} based on self.context
        self.name = objectName(self.context)
        self.container = getParent(self.context)
        if self.container is None and self.name == "":
            # Hack to get loading the root to work
            self.container = getRoot(self.context)
            self.fspath = os.path.join(self.tempdir, "root")
        else:
            self.fspath = os.path.join(self.tempdir, self.name)

    def make_metadata(self):
        self.metadata = Metadata()

    def call_checker(self):
        c = Checker(self.metadata)
        c.check(self.container, self.name, self.fspath)
        self.errors = c.errors()

    def send_errors(self):
        self.txn.abort()
        lines = ["Up-to-date check failed:"]
        tempdir_sep = os.path.join(self.tempdir, "") # E.g. foo -> foo/
        for e in self.errors:
            lines.append(e.replace(tempdir_sep, ""))
        lines.append("")
        self.request.response.setHeader("Content-Type", "text/plain")
        return "\n".join(lines)

    def call_committer(self):
        c = Committer(self.metadata)
        c.synch(self.container, self.name, self.fspath)

    def write_to_filesystem(self):
        shutil.rmtree(self.tempdir) # Start with clean slate
        os.mkdir(self.tempdir)
        toFS(self.context, objectName(self.context) or "root", self.tempdir)

    def send_archive(self):
        return snarf_dir(self.request.response, self.tempdir)
