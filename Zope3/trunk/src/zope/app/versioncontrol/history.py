##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Version History Support

$Id$
"""
import sys
import time

import persistent

from BTrees.IOBTree import IOBTree
from BTrees.IIBTree import IIBTree
from BTrees.OOBTree import OOBTree

import zope.app.location

import zope.app.versioncontrol.utility
import zope.app.versioncontrol.version

from zope.app.versioncontrol.interfaces import VersionControlError


class VersionHistory(persistent.Persistent, zope.app.location.Location):
    """A version history maintains the information about the changes
    to a particular version-controlled resource over time."""

    def __init__(self, history_id):
        # The _versions mapping maps version ids to version objects. All
        # of the actual version data is looked up there. The _labels
        # mapping maps labels to specific version ids. The _branches map
        # manages BranchInfo objects that maintain branch information.
        self._eventLog = EventLog()
        self._versions = OOBTree()
        self._branches = OOBTree()
        self._labels = OOBTree()
        mainline = self.createBranch('mainline', None)
        self.__name__ = history_id

    def addLogEntry(self, version_id, action, path=None, message=''):
        """Add a new log entry associated with this version history."""
        entry = LogEntry(version_id, action, path, message)
        self._eventLog.addEntry(entry)

    def getLogEntries(self):
        """Return a sequence of the log entries for this version history."""
        return self._eventLog.getEntries()

    def getLabels(self):
        return self._labels.keys()

    def labelVersion(self, version_id, label, force=0):
        """Associate a particular version in a version history with the
           given label, removing any existing association with that label
           if force is true, or raising an error if force is false and
           an association with the given label already exists."""
        current = self._labels.get(label)
        if current is not None:
            if current == version_id:
                return
            if not force:
                raise VersionControlError(
                    'The label %s is already associated with a version.' % (
                     label
                    ))
            del self._labels[label]
        self._labels[label] = version_id

    def createBranch(self, branch_id, version_id):
        """Create a new branch associated with the given branch_id. The
           new branch is rooted at the version named by version_id."""
        if self._branches.has_key(branch_id):
            raise VersionControlError(
                'Activity already exists: %s' % branch_id
                )
        branch = BranchInfo(branch_id, version_id)
        branch.__parent__ = self
        self._branches[branch_id] = branch
        return branch

    def createVersion(self, object, branch_id):
        """Create a new version in the line of descent named by the given
           branch_id, returning the newly created version object."""
        branch = self._branches.get(branch_id)
        if branch is None:
            branch = self.createBranch(branch_id, None)
        if branch.__name__ != 'mainline':
            version_id = '%s.%d' % (branch.__name__, len(branch) + 1)
        else:
            version_id = '%d' % (len(branch) + 1)
        version = zope.app.versioncontrol.version.Version(version_id)

        # Update the  predecessor, successor and branch relationships.
        # This is something of a hedge against the future. Versions will
        # always know enough to reconstruct their lineage without the help
        # of optimized data structures, which will make it easier to change
        # internals in the future if we need to.
        latest = branch.latest()
        if latest is not None:
            last = self._versions[latest]
            last.next = last.next + (version_id,)
            version.prev = latest

        # If the branch is not the mainline, store the branch name in the
        # version. Versions have 'mainline' as the default class attribute
        # which is the common case and saves a minor bit of storage space.
        if branch.__name__ != 'mainline':
            version.branch = branch.__name__

        branch.append(version)
        self._versions[version_id] = version
        # Call saveState() only after version has been linked into the
        # database, ensuring it goes into the correct database.
        version.saveState(object)
        version.__parent__ = self
        return version

    def hasVersionId(self, version_id):
        """Return true if history contains a version with the given id."""
        return self._versions.has_key(version_id)

    def isLatestVersion(self, version_id, branch_id):
        """Return true if version id is the latest in its branch."""
        branch = self._branches[branch_id]
        return version_id == branch.latest()

    def getLatestVersion(self, branch_id):
        """Return the latest version object within the given branch, or
        None if the branch contains no versions.
        """
        branch = self._branches[branch_id]
        version = self._versions[branch.latest()]
        return version

    def findBranchId(self, version_id):
        """Given a version id, return the id of the branch of the version.
        Note that we cheat, since we can find this out from the id.
        """
        parts = version_id.split('.')
        if len(parts) > 1:
            return parts[-2]
        return 'mainline'

    def getVersionById(self, version_id):
        """Return the version object named by the given version id, or
        raise a VersionControlError if the version is not found.
        """
        version = self._versions.get(version_id)
        if version is None:
            raise VersionControlError(
                'Unknown version id: %s' % version_id
                )
        return version

    def getVersionByLabel(self, label):
        """Return the version associated with the given label, or None
        if no version matches the given label.
        """
        version_id = self._labels.get(label)
        version = self._versions.get(version_id)
        if version is None:
            return None
        return version

    def getVersionByDate(self, branch_id, timestamp):
        """Return the last version committed in the given branch on or
        before the given time value. The timestamp should be a float
        (time.time format) value in UTC.
        """
        branch = self._branches[branch_id]
        tvalue = int(timestamp / 60.0)
        while 1:
            # Try to find a version with a commit date <= the given time
            # using the timestamp index in the branch information.
            if branch.m_order:
                try:
                    match = branch.m_date.maxKey(tvalue)
                    match = branch.m_order[branch.m_date[match]]
                    return self._versions[match]
                except ValueError:
                    pass

            # If we've run out of lineage without finding a version with
            # a commit date <= the given timestamp, we return None. It is
            # up to the caller to decide what to do in this situation.
            if branch.root is None:
                return None
            
            # If the branch has a root (a version in another branch), then
            # we check the root and do it again with the ancestor branch.
            rootver = self._versions[branch.root]
            if int(rootver.date_created / 60.0) < tvalue:
                return rootver
            branch = self._branches[rootver.branch]

    def getVersionIds(self, branch_id=None):
        """Return a sequence of version ids for versions in this history.

        If a branch_id is given, only version ids from that branch
        will be returned. Note that the sequence of ids returned does
        not include the id of the branch root.
        """
        if branch_id is not None:
            return self._branches[branch_id].versionIds()
        return self._versions.keys()


class BranchInfo(persistent.Persistent, zope.app.location.Location):
    """A utility class to hold branch (line-of-descent) information.

    It maintains the name of the branch, the version id of the root of
    the branch and indices to allow for efficient lookups.
    """

    def __init__(self, name, root):
        # m_order maintains a newest-first mapping of int -> version id.
        # m_date maintains a mapping of a packed date (int # of minutes
        # since the epoch) to a lookup key in m_order. The two structures
        # are separate because we only support minute precision for date
        # lookups (and multiple versions could be added in a minute).
        self.date_created = time.time()
        self.m_order = IOBTree()
        self.m_date = IIBTree()
        self.__name__ = name
        self.root = root

    def append(self, version):
        """Append a version to the branch information.

        Note that this does not store the actual version, but metadata
        about the version to support ordering and date lookups.
        """ 
        if len(self.m_order):
            key = self.m_order.minKey() - 1
        else:
            key = sys.maxint
        self.m_order[key] = version.__name__
        timestamp = int(version.date_created / 60.0)
        self.m_date[timestamp] = key

    def versionIds(self):
        """Return a newest-first sequence of version ids in the branch."""
        return self.m_order.values()

    def latest(self):
        """Return the version id of the latest version in the branch."""
        mapping = self.m_order
        if not len(mapping):
            return self.root
        return mapping[mapping.keys()[0]]

    def __len__(self):
        return len(self.m_order)


class EventLog(persistent.Persistent):
    """An EventLog encapsulates a collection of log entries."""

    def __init__(self):
        self._data = IOBTree()

    def addEntry(self, entry):
        """Add a new log entry."""
        if len(self._data):
            key = self._data.minKey() - 1
        else:
            key = sys.maxint
        self._data[key] = entry

    def getEntries(self):
        """Return a sequence of log entries."""
        return self._data.values()

    def __len__(self):
        return len(self._data)
    
    def __nonzero__(self):
        return bool(self._data)


class LogEntry(persistent.Persistent):
    """A LogEntry contains audit information about a version control
    operation. Actions that cause audit records to be created include
    checkout and checkin. Log entry information can be read (but not
    changed) by restricted code."""

    def __init__(self, version_id, action, path=None, message=''):
        self.timestamp = time.time()
        self.version_id = version_id
        self.action = action
        self.message = message
        self.user_id = zope.app.versioncontrol.utility._findUserId()
        self.path = path
