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
"""Higher-level three-way file and directory merger.

$Id: fsmerger.py,v 1.2 2003/05/15 15:32:23 gvanrossum Exp $
"""

import os

from os.path import exists, isfile, isdir, split, join
from os.path import realpath, normcase, normpath

from zope.fssync.merger import Merger
from zope.fssync import fsutil

class FSMerger(object):

    """Higher-level three-way file and directory merger."""

    def __init__(self, metadata, reporter):
        """Constructor.

        Arguments are a metadata database and a reporting function.
        """
        self.metadata = metadata
        self.reporter = reporter
        self.merger = Merger(metadata)

    def merge(self, local, remote):
        """Merge remote file or directory into local file or directory."""
        if ((isfile(local) or not exists(local))
            and
            (isfile(remote) or not exists(remote))):
            self.merge_files(local, remote)
        elif ((isdir(local) or not exists(local))
              and
              (isdir(remote) or not exists(remote))):
            self.merge_dirs(local, remote)
        else:
            # One is a file, the other is a directory
            # XXX We should be able to deal with this case, too
            self.reporter("XXX %s" % local)
        self.merge_extra(local, remote)
        self.merge_annotations(local, remote)

    def merge_extra(self, local, remote):
        lextra = fsutil.getextra(local)
        rextra = fsutil.getextra(remote)
        self.merge_dirs(lextra, rextra)

    def merge_annotations(self, local, remote):
        lannotations = fsutil.getannotations(local)
        rannotations = fsutil.getannotations(remote)
        self.merge_dirs(lannotations, rannotations)

    def merge_files(self, local, remote):
        """Merge remote file into local file."""
        original = fsutil.getoriginal(local)
        action, state = self.merger.classify_files(local, original, remote)
        state = self.merger.merge_files(local, original, remote,
                                        action, state) or state
        self.reportaction(action, state, local)

    def merge_dirs(self, localdir, remotedir):
        """Merge remote directory into local directory."""
        lnames = self.metadata.getnames(localdir)
        rnames = self.metadata.getnames(remotedir)
        lentry = self.metadata.getentry(localdir)
        rentry = self.metadata.getentry(remotedir)

        if not lnames and not rnames:

            if not lentry:
                if not rentry:
                    if exists(localdir):
                        self.reportdir("?", localdir)
                else:
                    if not exists(localdir):
                        fsutil.ensuredir(localdir)
                        self.reportdir("N", localdir)
                    else:
                        self.reportdir("*", localdir)
                return

            if lentry.get("flag") == "added":
                if not rentry:
                    self.reportdir("A", localdir)
                else:
                    self.reportdir("U", localdir)
                    del lentry["flag"]
                return

            if lentry.get("flag") == "removed":
                if rentry:
                    self.reportdir("R", localdir)
                else:
                    self.reportdir("D", localdir)
                    lentry.clear()
                return

            if not rentry:
                try:
                    os.rmdir(localdir)
                except os.error:
                    pass
                self.reportdir("D", localdir)
                lentry.clear()
                return

        if exists(localdir):
            self.reportdir("/", localdir)
            lnames = dict([(normcase(name), name)
                           for name in os.listdir(localdir)])
        else:
            if lentry.get("flag") != "removed" and (rentry or rnames):
                fsutil.ensuredir(localdir)
                lentry.update(rentry)
                self.reportdir("N", localdir)
            lnames = {}

        if exists(remotedir):
            rnames = dict([(normcase(name), name)
                           for name in os.listdir(remotedir)])
        else:
            rnames = {}

        names = {}
        names.update(lnames)
        names.update(rnames)
        if fsutil.nczope in names:
            del names[fsutil.nczope]

        ncnames = names.keys()
        ncnames.sort()
        for ncname in ncnames:
            name = names[ncname]
            self.merge(join(localdir, name), join(remotedir, name))

    def reportdir(self, letter, localdir):
        """Helper to report something for a directory.

        This adds a separator (e.g. '/') to the end of the pathname to
        signal that it is a directory.
        """
        self.reporter("%s %s" % (letter, join(localdir, "")))

    def reportaction(self, action, state, local):
        """Helper to report an action and a resulting state.

        This always results in exactly one line being reported.
        Report letters are:

        C -- conflicting changes not resolved (not committed)
        U -- file brought up to date (possibly created)
        M -- modified (not committed)
        A -- added (not committed)
        R -- removed (not committed)
        D -- file deleted
        ? -- file exists locally but not remotely
        * -- nothing happened
        """
        assert action in ('Fix', 'Copy', 'Merge', 'Delete', 'Nothing'), action
        assert state in ('Conflict', 'Uptodate', 'Modified', 'Spurious',
                         'Added', 'Removed', 'Nonexistent'), state
        letter = "*"
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
                letter = "D"
        if letter:
            self.reporter("%s %s" % (letter, local))

    def ignore(self, path):
        # XXX This should have a larger set of default patterns to
        # ignore, and honor .cvsignore
        return path.endswith("~")
