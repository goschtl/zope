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

$Id: fssync.py,v 1.15 2003/06/02 20:44:41 gvanrossum Exp $
"""

import os
import shutil
import tempfile

from transaction import get_transaction

from zope.publisher.browser import BrowserView
from zope.app.traversing import objectName, getParent, getRoot
from zope.app.interfaces.exceptions import UserError
from zope.fssync.snarf import Snarfer, Unsnarfer
from zope.app.fssync.syncer import toFS
from zope.app.fssync.committer import Committer
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
        if not self.request.getHeader("Content-Type") == "application/x-snarf":
            self.request.response.setHeader("Content-Type", "text/plain")
            return "ERROR: Content-Type is not application/x-snarf\n"
        txn = get_transaction() # Save for later
        # 00) Set transaction note
        note = self.request.get("note")
        if not note:
            # XXX Hack because cgi doesn't parse the query string
            qs = self.request._environ.get("QUERY_STRING")
            if qs and qs.startswith("note="):
                note = qs[5:]
                import urllib
                note = urllib.unquote(note)
        if note:
            txn.note(note)
        # 0) Allocate temporary names
        working = tempfile.mktemp()
        try:
            # 1) Create the working directory
            os.mkdir(working)
            # 2) Unsnarf into the working directory
            istr = self.request.bodyFile
            istr.seek(0)
            uns = Unsnarfer(istr)
            uns.unsnarf(working)
            # 3) Commit; this includes the uptodate check and updates
            name = objectName(self.context)
            container = getParent(self.context)
            if container is None and name == "":
                # Hack to get loading the root to work
                container = getRoot(self.context)
                fspath = os.path.join(working, "root")
            else:
                fspath = os.path.join(working, name)
            md = Metadata()
            c = Committer(md)
            c.synch(container, name, fspath)
            # 4) Generate response (snarfed archive or error text)
            errors = c.get_errors()
            if not errors:
                # The flush() isn't really needed, but it's better to
                # waste some cycles now than to have this corrupt some
                # files later.
                md.flush()
                # Do a fresh toFS(), to be sure to get all changes
                shutil.rmtree(working)
                os.mkdir(working)
                toFS(self.context, objectName(self.context) or "root", working)
                return snarf_dir(self.request.response, working)
            else:
                txn.abort()
                lines = ["Up-to-date check failed:"]
                working_sep = os.path.join(working, "") # E.g. foo -> foo/
                for e in errors:
                    lines.append(e.replace(working_sep, ""))
                lines.append("")
                self.request.response.setHeader("Content-Type", "text/plain")
                return "\n".join(lines)
        finally:
            if os.path.exists(working):
                shutil.rmtree(working)
