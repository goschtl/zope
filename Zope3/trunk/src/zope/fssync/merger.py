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
"""Class to do augmented three-way merges.

This boils down to distinguishing an astonishing number of cases.

$Id: merger.py,v 1.1 2003/05/12 20:19:38 gvanrossum Exp $
"""

import os
import shutil
import filecmp
import commands

from os.path import exists, isdir, isfile

class Merger(object):
    """Augmented three-way file and directory merges.

    An augmented merge takes into account three files (or directories)
    and two metadata entries.  The files are labeled local, original,
    and remote.  The metadata entries are for local and remote.  A
    remote metadata entry is either empty or non-empty.  Empty means
    the file does not exist remotely, non-empty means it does exist
    remotely.  We also have to take into account the possibility that
    the existence of the file belies what the entry declares.  A local
    metadata entry can have those states, and in addition, if
    non-empty, it can be flagged as added or removed.  Again, the
    existence of the file may bely what the entry claims.  The
    original file serves the obvious purpose.  Its existence, too, can
    be inconsistent with the state indicated by the metadata entries.

    To find the metadata entry for a file, we look for a key
    corresponding to its basename @@Zope/Entries.xml in the directory
    that contains it.  For this purpose, we assume the filename given
    uses the correct case even on a case-insensitive filesystem (i.e.,
    the filesystem must be at least case-preserving).

    The purpose of the merge() function is to merging the remote
    changes into the local copy as the best it can, resolving
    inconsistencies if possible.  It should not raise an exception
    unless there are file/directory permission problems.  Its return
    value is an indicator of what it dit.

    The classify() function is a helper for merge(); it looks at all
    the evidence and decides what merge() should do, without actually
    touching any files or the metadata.  Possible actions are:

    Fix      -- copy the remote copy to the local original, nothing else
    Copy     -- copy the remote copy over the local copy
    Merge    -- merge the remote copy into the local copy
                (this may cause merge conflicts when tried)
    Delete   -- delete the local copy
    Nothing  -- do nothing

    The original file is made a copy of the remote file for actions
    Fix, Copy and Merge; it is deleted for action Delete; it is
    untouched for action Nothing.

    It should also indicate the final state of the local copy after
    the action is taken:

    Conflict -- there is a conflict of some kind
    Uptodate -- the local copy is the same as the remote copy
    Modified -- the local copy is marked (to be) modified
    Added    -- the local copy is marked (to be) added
    Removed  -- the local copy is marked (to be) removed
    Spurious -- there is an unregistered local file only
    Nonexistent -- there is nothing locally or remotely

    For Conflict, Added and Removed, the action will always be
    Nothing.  The difference between Removed and Nonexistent is that
    Nonexistent means the file doesn't exist remotely either, while
    Removed means that on the next commit the file should be removed
    from the remote store.  Similarly, Added means the file should be
    added remotely on the next commit, and Modified means that the
    file should be changed remotely to match the local copy at the
    next commit.

    Note that carrying out the Merge action can change the resulting
    state to become Uptodate or Conflict instead of Modified, if there
    are merge conflicts (which classify() can't detect without doing
    more work than reasonable).
    """

    def __init__(self, metadata, verbose=True):
        """Constructor.

        The argument is the metadata database, which has a single
        method: getentry(file) which returns a dict containing the
        metadata for that file.  Changes to this dict will be
        preserved when the database is written back (not by the Merger
        class).  To delete all metadata for a file, call the dict's
        clear() method.
        """
        self.metadata = metadata
        self.verbose = verbose

    def getentry(self, file):
        """Helper to abstract away the existence of self.metadata."""
        # XXX Hmm...  This could be a subclass of class Metadata...
        return self.metadata.getentry(file)

    def merge_files(self, local, orig, remote, action, state):
        """Helper to carry out a file merge.

        The action and state arguments correspond to the return value
        of classify().

        Return the state as returned by the second return value of
        classify().  This is either the argument state or recalculated
        based upon the effect of the action.
        """
        method = getattr(self, "merge_files_" + action.lower())
        return method(local, orig, remote) or state

    def merge_files_nothing(self, local, orig, remote):
        return None

    def merge_files_remove(self, local, orig, remote):
        if isfile(local):
            os.remove(local)
        if isfile(orig):
            os.remove(orig)
        self.getentry(local).clear()
        return None

    def merge_files_copy(self, local, orig, remote):
        shutil.copy(remote, local)
        shutil.copy(remote, orig)
        self.getentry(local).update(self.getentry(remote))
        self.clearflag(local)
        return None

    def merge_files_merge(self, local, orig, remote):
        # XXX This is platform dependent
        if exists(orig):
            origfile = orig
        else:
            origfile = "/dev/null"
        cmd = "merge %s %s %s" % (commands.mkarg(local),
                                  commands.mkarg(origfile),
                                  commands.mkarg(remote))
        sts, output = commands.getstatusoutput(cmd)
        if output and self.verbose:
            print output
        shutil.copy(remote, orig)
        self.getentry(local).update(self.getentry(remote))
        self.clearflag(local)
        if sts:
            self.getentry(local)["conflict"] = os.path.getmtime(local)
            return "Conflict"
        else:
            return "Modified"

    def merge_files_fix(self, local, orig, remote):
        shutil.copy(remote, orig)
        self.clearflag(local)
        self.getentry(local).update(self.getentry(remote))

    def clearflag(self, file):
        """Helper to clear the added/removed metadata flag."""
        metadata = self.getentry(file)
        if "flag" in metadata:
            del metadata["flag"]

    def classify_files(self, local, orig, remote):
        """Helper for merge to classify file changes.

        Arguments are pathnames to the local, original, and remote
        copies.

        Return a pair of strings (action, state) where action is one
        of 'Fix', 'Copy', 'Merge', 'Delete' or 'Nothing', and state is
        one of 'Conflict', 'Uptodate', 'Modified', 'Added', 'Removed'
        or 'Nonexistent'.
        
        """
        lmeta = self.getentry(local)
        rmeta = self.getentry(remote)

        # Sort out cases involving additions or removals

        if not lmeta and not rmeta:
            if exists(local):
                # Local unregistered file
                return ("Nothing", "Spurious")
            else:
                # Why are we here?
                return ("Nothing", "Nonexistent")

        if lmeta.get("flag") == "added":
            # Added locally
            if not rmeta:
                # Nothing remotely
                return ("Nothing", "Added")
            else:
                # Added remotely too!  Merge, unless trivial conflict
                if self.cmpfile(local, remote):
                    return ("Fix", "Uptodate")
                else:
                    return ("Merge", "Modified")

        if rmeta and not lmeta:
            # Added remotely
            return ("Copy", "Uptodate")

        if lmeta.get("flag") == "removed":
            if not rmeta:
                # Removed remotely too
                return ("Remove", "Nonexistent")
            else:
                # Removed locally
                if self.cmpfile(orig, remote):
                    return ("Nothing", "Removed")
                else:
                    return ("Nothing", "Conflict")

        if lmeta and not rmeta:
            assert lmeta.get("flag") is None
            # Removed remotely
            return ("Remove", "Nonexistent")

        if lmeta.get("flag") is None and not exists(local):
            # Lost locally
            if rmeta:
                return ("Copy", "Uptodate")
            else:
                return ("Remove", "Nonexistent")

        # Sort out cases involving simple changes to files

        if self.cmpfile(orig, remote):
            # No remote changes; classify local changes
            if self.cmpfile(local, orig):
                # No changes
                return ("Nothing", "Uptodate")
            else:
                # Only local changes
                return ("Nothing", "Modified")
        else:
            # Some local changes; classify local changes
            if self.cmpfile(local, orig):
                # Only remote changes
                return ("Copy", "Uptodate")
            else:
                if self.cmpfile(local, remote):
                    # We're lucky -- local and remote changes are the same
                    return ("Fix", "Uptodate")
                else:
                    # Changes on both sides, three-way merge needed
                    return ("Merge", "Modified")

    def cmpfile(self, file1, file2):
        """Helper to compare two files.

        Return True iff the files are equal.
        """
        # XXX What should this do when either file doesn't exist?
        return filecmp.cmp(file1, file2, shallow=False)
