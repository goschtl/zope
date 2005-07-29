##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Code for the toFS.snarf view and its inverse, fromFS.snarf.

$Id$
"""
__docformat__ = 'restructuredtext'

import os
import cgi
import shutil
import tempfile

import transaction

from zope.app.publisher.browser import BrowserView
from zope.app.traversing.api import getName, getParent, getRoot
from zope.fssync.snarf import Snarfer, Unsnarfer
from zope.app.fssync import syncer
from zope.app.fssync.committer import Committer, Checker
from zope.fssync.metadata import Metadata

from zope.app.i18n import ZopeMessageIDFactory as _

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
            syncer.toFS(self.context,
                        getName(self.context) or "root",
                        dirname)
            return snarf_dir(self.request.response, dirname)
        finally:
            if os.path.isdir(dirname):
                shutil.rmtree(dirname)

class NewMetadata(Metadata):
    """Subclass of Metadata that sets the ``added`` flag in all entries."""

    def getentry(self, file):
        entry = Metadata.getentry(self, file)
        if entry:
            entry["flag"] = "added"
        return entry


class SnarfSubmission(BrowserView):
    """Base class for the commit and checkin views."""

    def run(self):
        self.check_content_type()
        self.set_transaction()
        self.parse_args()
        self.set_note()
        try:
            self.make_tempdir()
            self.set_arguments()
            self.make_metadata()
            self.unsnarf_body()
            return self.run_submission()
        finally:
            self.remove_tempdir()

    def check_content_type(self):
        if not self.request.getHeader("Content-Type") == "application/x-snarf":
            raise ValueError(_("Content-Type is not application/x-snarf"))

    def set_transaction(self):
        self.txn = transaction.get()

    def parse_args(self):
        # The query string in the URL didn't get parsed, because we're
        # getting a POST request with an unrecognized content-type
        qs = self.request._environ.get("QUERY_STRING")
        if qs:
            self.args = cgi.parse_qs(qs)
        else:
            self.args = {}

    def get_arg(self, key):
        value = self.request.get(key)
        if value is None:
            values = self.args.get(key)
            if values is not None:
                value = " ".join(values)
        return value

    def set_note(self):
        note = self.get_arg("note")
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

    def call_committer(self):
        c = Committer(syncer.getSerializer, self.metadata,
                      getAnnotations=syncer.getAnnotations)
        c.synch(self.container, self.name, self.fspath)


class SnarfCheckin(SnarfSubmission):
    """View for checking a new sub-tree into Zope.

    The input should be a POST request whose data is a snarf archive.
    This creates a brand new tree and doesn't return anything.
    """

    def run_submission(self):
        # XXX need to make sure the top-level name doesn't already
        # exist, or existing site data can get screwed
        self.call_committer()
        return ""

    def set_arguments(self):
        # Compute self.{name, container, fspath} for checkin()
        name = self.get_arg("name")
        if not name:
            raise ValueError(_("required argument 'name' missing"))
        src = self.get_arg("src")
        if not src:
            src = name
        self.container = self.context
        self.name = name
        self.fspath = os.path.join(self.tempdir, src)

    def make_metadata(self):
        self.metadata = NewMetadata()


class SnarfCommit(SnarfSubmission):
    """View for committing changes to an existing tree.

    The input should be a POST request whose data is a snarf archive.
    It returns an updated snarf archive, or a text document with
    errors.
    """

    def run_submission(self):
        self.call_checker()
        if self.errors:
            return self.send_errors()
        else:
            self.call_committer()
            self.write_to_filesystem()
            return self.send_archive()

    def set_arguments(self):
        # Compute self.{name, container, fspath} for commit()
        self.name = getName(self.context)
        self.container = getParent(self.context)
        if self.container is None and self.name == "":
            # Hack to get loading the root to work
            self.container = getRoot(self.context)
            self.fspath = os.path.join(self.tempdir, "root")
        else:
            self.fspath = os.path.join(self.tempdir, self.name)

    def make_metadata(self):
        self.metadata = Metadata()

    def get_checker(self, raise_on_conflicts=False):
        return Checker(syncer.getSerializer,
                       self.metadata,
                       raise_on_conflicts,
                       getAnnotations=syncer.getAnnotations)

    def call_checker(self):
        if self.get_arg("raise"):
            c = self.get_checker(True)
        else:
            c = self.get_checker()
        c.check(self.container, self.name, self.fspath)
        self.errors = c.errors()

    def send_errors(self):
        self.txn.abort()
        lines = [_("Up-to-date check failed:")]
        tempdir_sep = os.path.join(self.tempdir, "") # E.g. foo -> foo/
        for e in self.errors:
            lines.append(e.replace(tempdir_sep, ""))
        lines.append("")
        self.request.response.setHeader("Content-Type", "text/plain")
        return "\n".join(lines)

    def write_to_filesystem(self):
        shutil.rmtree(self.tempdir) # Start with clean slate
        os.mkdir(self.tempdir)
        syncer.toFS(self.context,
                    getName(self.context) or "root",
                    self.tempdir)

    def send_archive(self):
        return snarf_dir(self.request.response, self.tempdir)
