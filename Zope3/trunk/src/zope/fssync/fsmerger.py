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

$Id: fsmerger.py,v 1.15 2003/08/17 06:08:56 philikon Exp $
"""

import os
import shutil

from os.path import exists, isfile, isdir, join
from os.path import realpath, normcase, normpath

from zope.xmlpickle import dumps

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
            # XXX probably for the best; we *don't* know the right
            # thing to do anyway
            return
        self.merge_extra(local, remote)
        self.merge_annotations(local, remote)
        if not exists(local) and not self.metadata.getentry(local):
            self.remove_special(local, "Extra")
            self.remove_special(local, "Annotations")
            self.remove_special(local, "Original")

    def merge_extra(self, local, remote):
        """Helper to merge the Extra trees."""
        lextra = fsutil.getextra(local)
        rextra = fsutil.getextra(remote)
        self.merge_dirs(lextra, rextra)

    def merge_annotations(self, local, remote):
        """Helper to merge the Anotations trees."""
        lannotations = fsutil.getannotations(local)
        rannotations = fsutil.getannotations(remote)
        self.merge_dirs(lannotations, rannotations)

    def remove_special(self, local, what):
        """Helper to remove an Original, Extra or Annotations file/tree."""
        head, tail = fsutil.split(local)
        dir = join(head, "@@Zope", what)
        target = join(dir, tail)
        if exists(target):
            if isdir(target):
                shutil.rmtree(target)
            else:
                os.remove(target)
        if isdir(dir):
            try:
                os.rmdir(dir)
            except os.error:
                pass

    def merge_files(self, local, remote):
        """Merge remote file into local file."""

        # Reset sticky conflict if file was edited or removed
        entry = self.metadata.getentry(local)
        conflict = entry.get("conflict")
        if conflict and not os.path.exists(local):
            del entry["conflict"]

        original = fsutil.getoriginal(local)
        action, state = self.merger.classify_files(local, original, remote)
        state = self.merger.merge_files(local, original, remote,
                                        action, state) or state
        self.reportaction(action, state, local)

    def merge_dirs(self, localdir, remotedir):
        """Merge remote directory into local directory."""
        lentrynames = self.metadata.getnames(localdir)
        rentrynames = self.metadata.getnames(remotedir)
        lentry = self.metadata.getentry(localdir)
        rentry = self.metadata.getentry(remotedir)

        if not lentrynames and not rentrynames:

            if not lentry:
                if not rentry:
                    if exists(localdir):
                        self.reportdir("?", localdir)
                else:
                    if not exists(localdir):
                        self.make_dir(localdir)
                        lentry.update(rentry)
                        self.reportdir("N", localdir)
                    else:
                        # call make_dir() to create @@Zope and store metadata
                        self.make_dir(localdir)
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
                self.clear_dir(localdir)
                return

        if exists(localdir):
            if lentry.get("flag") == "added":
                if exists(remotedir):
                    self.reportdir("U", localdir)
                    del lentry["flag"]
                else:
                    self.reportdir("A", localdir)
            else:
                if rentry or exists(remotedir):
                    self.reportdir("/", localdir)
                else:
                    # Tree removed remotely, must recurse down locally
                    for name in lentrynames:
                        # merge() removes the local copies since the
                        # remote versions are gone, unless there have
                        # been local changes.
                        self.merge(join(localdir, name), join(remotedir, name))
                    self.clear_dir(localdir)
                    return

            lnames = dict([(normcase(name), name)
                           for name in os.listdir(localdir)])
        else:
            flag = lentry.get("flag")
            if flag == "removed":
                self.reportdir("R", localdir)
                return # There's no point in recursing down!
            if rentry or rentrynames:
                # remote directory is new
                self.make_dir(localdir)
                lentry.update(rentry)
                self.reportdir("N", localdir)
            lnames = {}

        for name in lentrynames:
            lnames[normcase(name)] = name

        if exists(remotedir):
            rnames = dict([(normcase(name), name)
                           for name in os.listdir(remotedir)])
        else:
            rnames = {}

        for name in rentrynames:
            rnames[normcase(name)] = name

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

    def make_dir(self, localdir):
        """Helper to create a local directory.

        This also creates the @@Zope subdirectory and places an empty
        Entries.xml file in it.
        """
        fsutil.ensuredir(localdir)
        localzopedir = join(localdir, "@@Zope")
        fsutil.ensuredir(localzopedir)
        efile = join(localzopedir, "Entries.xml")
        if not os.path.exists(efile):
            data = dumps({})
            f = open(efile, "w")
            try:
                f.write(data)
            finally:
                f.close()

    def clear_dir(self, localdir):
        """Helper to get rid of a local directory.

        This zaps the directory's @@Zope subdirectory, but not other
        files/directories that might still exist.

        It doesn't deal with extras and annotations for the directory
        itself, though.
        """
        lentry = self.metadata.getentry(localdir)
        lentry.clear()
        localzopedir = join(localdir, "@@Zope")
        if os.path.isdir(localzopedir):
            shutil.rmtree(localzopedir)
        try:
            os.rmdir(localdir)
        except os.error:
            self.reportdir("?", localdir)
        else:
            self.reportdir("D", localdir)

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
        self.reporter("%s %s" % (letter, local))

    def ignore(self, path):
        # XXX This should have a larger set of default patterns to
        # ignore, and honor .cvsignore
        return path.endswith("~")
