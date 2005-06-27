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
"""Version Control Repository

$Id$
"""
import datetime
import time
from random import randint

import persistent
from BTrees.OOBTree import OOBTree
from BTrees.OIBTree import OIBTree

import zope.event
import zope.interface

from zope.app import datetimeutils
from zope.app import zapi

from zope.app.annotation.interfaces import IAnnotations

from zope.app.versioncontrol import event
from zope.app.versioncontrol.history import VersionHistory
from zope.app.versioncontrol.interfaces import VersionControlError
from zope.app.versioncontrol.interfaces import IVersionable, IVersioned
from zope.app.versioncontrol.interfaces import IRepository
from zope.app.versioncontrol.interfaces import CHECKED_IN, CHECKED_OUT
from zope.app.versioncontrol.interfaces import ACTION_CHECKIN, ACTION_CHECKOUT
from zope.app.versioncontrol.interfaces import ACTION_UNCHECKOUT, ACTION_UPDATE
from zope.app.versioncontrol import nonversioned
from zope.app.versioncontrol import utility


VERSION_INFO_KEY = "%s.%s" % (utility.__name__, utility.VersionInfo.__name__)


class Repository(persistent.Persistent):
    """The repository implementation manages the actual data of versions
    and version histories. It does not handle user interface issues."""

    zope.interface.implements(IRepository)

    def __init__(self):
        # These keep track of symbolic label and branch names that
        # have been used to ensure that they don't collide.
        self._branches = OIBTree()
        self._branches['mainline'] = 1
        self._labels = OIBTree()

        self._histories = OOBTree()
        self._created = datetime.datetime.utcnow()

    def createVersionHistory(self):
        """Internal: create a new version history for a resource."""
        # When one creates the first version in a version history, neither
        # the version or version history yet have a _p_jar, which causes
        # copy operations to fail. To work around that, we share our _p_jar.
        history_id = None
        while history_id is None or self._histories.has_key(history_id):
            history_id = str(randint(1, 9999999999))
        history = VersionHistory(history_id)
        history.__parent__ = self
        self._histories[history_id] = history
        return history

    def getVersionHistory(self, history_id):
        """Internal: return a version history given a version history id."""
        return self._histories[history_id]

    def replaceState(self, obj, new_state):
        """Internal: replace the state of a persistent object.
        """
        non_versioned = nonversioned.getNonVersionedData(obj)
        # XXX There ought to be some way to do this more cleanly.
        # This fills the __dict__ of the old object with new state.
        # The other way to achieve the desired effect is to replace
        # the object in its container, but this method preserves the
        # identity of the object.
        if obj.__class__ is not new_state.__class__:
            raise VersionControlError(
                "The class of the versioned object has changed. %s != %s"
                % (repr(obj.__class__, new_state.__class__)))
        obj._p_changed = 1
        obj.__dict__.clear()
        obj.__dict__.update(new_state.__dict__)
        if non_versioned:
            # Restore the non-versioned data into the new state.
            nonversioned.restoreNonVersionedData(obj, non_versioned)
        return obj

    #####################################################################
    # This is the implementation of the public version control interface.
    #####################################################################

    def isResourceUpToDate(self, object, require_branch=False):
        info = self.getVersionInfo(object)
        history = self.getVersionHistory(info.history_id)
        branch = 'mainline'
        if info.sticky:
            if info.sticky[0] == 'B':
                branch = info.sticky[1]
            elif require_branch:
                # The object is updated to a particular version
                # rather than a branch.  The caller
                # requires a branch.
                return False
        return history.isLatestVersion(info.version_id, branch)

    def isResourceChanged(self, object):
        # Return true if the state of a resource has changed in a transaction
        # *after* the version bookkeeping was saved. Note that this method is
        # not appropriate for detecting changes within a transaction!
        info = self.getVersionInfo(object)
        info.version_id # deghostify info
        itime = getattr(info, '_p_serial', None)
        if itime is None:
            return False
        mtime = utility._findModificationTime(object)
        if mtime is None:
            return False
        return mtime > itime

    def getVersionInfo(self, object):
        # Return the VersionInfo associated with the given object.
        #
        # The VersionInfo object contains version control bookkeeping
        # information.  If the object is not under version control, a
        # VersionControlError will be raised.
        #
        if IVersioned.providedBy(object):
            annotations = IAnnotations(object)
            return annotations[VERSION_INFO_KEY]
        raise VersionControlError(
            "Object is not under version control.")

    def queryVersionInfo(self, object, default=None):
        if IVersioned.providedBy(object):
            annotations = IAnnotations(object)
            return annotations[VERSION_INFO_KEY]
        return default

    def applyVersionControl(self, object, message=None):
        if IVersioned.providedBy(object):
            raise VersionControlError(
                'The resource is already under version control.'
                )
        if not IVersionable.providedBy(object):
            raise VersionControlError(
                'This resource cannot be put under version control.'
                )

        # Need to check the parent to see if the container of the object
        # being put under version control is itself a version-controlled
        # object. If so, we need to use the branch id of the container.
        branch = 'mainline'
        parent = getattr(object, '__parent__', None)
        if parent is None:
            p_info = None
        else:
            p_info = self.queryVersionInfo(parent)
        if p_info is not None:
            sticky = p_info.sticky
            if sticky and sticky[0] == 'B':
                branch = sticky[1]

        # Create a new version history and initial version object.
        history = self.createVersionHistory()
        version = history.createVersion(object, branch)

        history_id = history.__name__
        version_id = version.__name__

        # Add bookkeeping information to the version controlled object.
        declare_versioned(object)
        info = utility.VersionInfo(history_id, version_id, CHECKED_IN)
        annotations = IAnnotations(object)
        annotations[VERSION_INFO_KEY] = info
        if branch != 'mainline':
            info.sticky = ('B', branch)

        # Save an audit record of the action being performed.
        history.addLogEntry(version_id,
                            ACTION_CHECKIN,
                            zapi.getPath(object),
                            message is None and 'Initial checkin.' or message
                            )

        zope.event.notify(event.VersionControlApplied(object, info, message))

    def checkoutResource(self, object):
        info = self.getVersionInfo(object)
        if info.status != CHECKED_IN:
            raise VersionControlError(
                'The selected resource is already checked out.'
                )

        if info.sticky and info.sticky[0] != 'B':
            raise VersionControlError(
                'The selected resource has been updated to a particular '
                'version, label or date. The resource must be updated to '
                'the mainline or a branch before it may be checked out.'
                )

        if not self.isResourceUpToDate(object):
            raise VersionControlError(
                'The selected resource is not up to date!'
                )

        history = self.getVersionHistory(info.history_id)
        ob_path = zapi.getPath(object)

        # Save an audit record of the action being performed.
        history.addLogEntry(info.version_id,
                            ACTION_CHECKOUT,
                            ob_path
                            )

        # Update bookkeeping information.
        info.status = CHECKED_OUT
        info.touch()

        zope.event.notify(event.VersionCheckedOut(object, info))

    def checkinResource(self, object, message=''):
        info = self.getVersionInfo(object)
        if info.status != CHECKED_OUT:
            raise VersionControlError(
                'The selected resource is not checked out.'
                )

        if info.sticky and info.sticky[0] != 'B':
            raise VersionControlError(
                'The selected resource has been updated to a particular '
                'version, label or date. The resource must be updated to '
                'the mainline or a branch before it may be checked in.'
                )

        if not self.isResourceUpToDate(object):
            raise VersionControlError(
                'The selected resource is not up to date!'
                )

        history = self.getVersionHistory(info.history_id)
        ob_path = zapi.getPath(object)

        branch = 'mainline'
        if info.sticky is not None and info.sticky[0] == 'B':
            branch = info.sticky[1]

        version = history.createVersion(object, branch)

        # Save an audit record of the action being performed.
        history.addLogEntry(version.__name__,
                            ACTION_CHECKIN,
                            ob_path,
                            message
                            )

        # Update bookkeeping information.
        info.version_id = version.__name__
        info.status = CHECKED_IN
        info.touch()

        zope.event.notify(event.VersionCheckedIn(object, info))

    def uncheckoutResource(self, object):
        info = self.getVersionInfo(object)
        if info.status != CHECKED_OUT:
            raise VersionControlError(
                'The selected resource is not checked out.'
                )

        history = self.getVersionHistory(info.history_id)
        ob_path = zapi.getPath(object)

        version = history.getVersionById(info.version_id)

        # Save an audit record of the action being performed.
        history.addLogEntry(info.version_id,
                            ACTION_UNCHECKOUT,
                            ob_path
                            )

        # Replace the state of the object with a reverted state.
        self.replaceState(object, version.copyState())

        # Update bookkeeping information.
        info = utility.VersionInfo(info.history_id, info.version_id,
                                   CHECKED_IN)
        annotations = IAnnotations(object)
        annotations[VERSION_INFO_KEY] = info

        zope.event.notify(event.VersionReverted(object, info))

    def updateResource(self, object, selector=None):
        info = self.getVersionInfo(object)
        if info.status != CHECKED_IN:
            raise VersionControlError(
                'The selected resource must be checked in to be updated.'
                )

        history = self.getVersionHistory(info.history_id)
        oldversion = info.version_id
        version = None
        sticky = info.sticky

        if not selector:
            # If selector is null, update to the latest version taking any
            # sticky attrs into account (branch, date). Note that the sticky
            # tag could also be a date or version id. We don't bother checking
            # for those, since in both cases we do nothing (because we'll
            # always be up to date until the sticky tag changes).
            if sticky and sticky[0] == 'L':
                # A label sticky tag, so update to that label (since it is
                # possible, but unlikely, that the label has been moved).
                version = history.getVersionByLabel(sticky[1])
            elif sticky and sticky[0] == 'B':
                # A branch sticky tag. Update to latest version on branch.
                version = history.getLatestVersion(selector)
            else:
                # Update to mainline, forgetting any date or version id
                # sticky tag that was previously associated with the object.
                version = history.getLatestVersion('mainline')
                sticky = None
        else:
            # If the selector is non-null, we find the version specified
            # and update the sticky tag. Later we'll check the version we
            # found and decide whether we really need to update the object.
            if history.hasVersionId(selector):
                version = history.getVersionById(selector)
                sticky = ('V', selector)

            elif self._labels.has_key(selector):
                version = history.getVersionByLabel(selector)
                sticky = ('L', selector)

            elif self._branches.has_key(selector):
                version = history.getLatestVersion(selector)
                if selector == 'mainline':
                    sticky = None
                else:
                    sticky = ('B', selector)
            else:
                try:    date = DateTime(selector)
                except:
                    raise VersionControlError(
                        'Invalid version selector: %s' % selector
                        )
                else:
                    timestamp = date.timeTime()
                    sticky = ('D', timestamp)
                    # Fix!
                    branch = history.findBranchId(info.version_id)
                    version = history.getVersionByDate(branch, timestamp)

        # If the state of the resource really needs to be changed, do the
        # update and make a log entry for the update.
        version_id = version and version.__name__ or info.version_id
        if version and (version_id != info.version_id):
            self.replaceState(object, version.copyState())
            declare_versioned(object)

            history.addLogEntry(version_id,
                                ACTION_UPDATE,
                                zapi.getPath(object)
                                )

        # Update bookkeeping information.
        info = utility.VersionInfo(info.history_id, version_id, CHECKED_IN)
        if sticky is not None:
            info.sticky = sticky
        annotations = IAnnotations(object)
        annotations[VERSION_INFO_KEY] = info

        zope.event.notify(event.VersionUpdated(object, info, oldversion))

    def labelResource(self, object, label, force=0):
        info = self.getVersionInfo(object)
        if info.status != CHECKED_IN:
            raise VersionControlError(
                'The selected resource must be checked in to be labeled.'
                )

        # Make sure that labels and branch ids do not collide.
        if self._branches.has_key(label) or label == 'mainline':
            raise VersionControlError(
                'The label value given is already in use as a branch id.'
                )
        if not self._labels.has_key(label):
            self._labels[label] = 1

        history = self.getVersionHistory(info.history_id)
        history.labelVersion(info.version_id, label, force)

        zope.event.notify(event.VersionLabelled(object, info, label))

    def makeBranch(self, object, branch_id=None):
        # Note - this is not part of the official version control API yet.
        # It is here to allow unit testing of the architectural aspects
        # that are already in place to support activities in the future.

        info = self.getVersionInfo(object)
        if info.status != CHECKED_IN:
            raise VersionControlError(
                'The selected resource must be checked in.'
                )

        history = self.getVersionHistory(info.history_id)

        if branch_id is None:
            i = 1
            while 1:
                branch_id = "%s.%d" % (info.version_id, i)
                if not (history._branches.has_key(branch_id)
                        or
                        self._labels.has_key(branch_id)
                        ):
                    break
                i += 1

        # Make sure that branch ids and labels do not collide.
        if self._labels.has_key(branch_id) or branch_id == 'mainline':
            raise VersionControlError(
                'The value given is already in use as a version label.'
                )

        if not self._branches.has_key(branch_id):
            self._branches[branch_id] = 1

        if history._branches.has_key(branch_id):
            raise VersionControlError(
                'The resource is already associated with the given branch.'
                )

        history.createBranch(branch_id, info.version_id)

        zope.event.notify(event.BranchCreated(object, info, branch_id))

        return branch_id

    def getVersionOfResource(self, history_id, selector):
        history = self.getVersionHistory(history_id)
        sticky = None

        if not selector or selector == 'mainline':
            version = history.getLatestVersion('mainline')
        else:
            if history.hasVersionId(selector):
                version = history.getVersionById(selector)
                sticky = ('V', selector)

            elif self._labels.has_key(selector):
                version = history.getVersionByLabel(selector)
                sticky = ('L', selector)

            elif self._branches.has_key(selector):
                version = history.getLatestVersion(selector)
                sticky = ('B', selector)
            else:
                try:
                    timestamp = datetimeutils.time(selector)
                except datetimeutils.DateTimeError:
                    raise VersionControlError(
                        'Invalid version selector: %s' % selector
                        )
                else:
                    sticky = ('D', timestamp)
                    version = history.getVersionByDate('mainline', timestamp)

        object = version.copyState()
        declare_versioned(object)

        info = utility.VersionInfo(history_id, version.__name__, CHECKED_IN)
        if sticky is not None:
            info.sticky = sticky
        annotations = IAnnotations(object)
        annotations[VERSION_INFO_KEY] = info

        zope.event.notify(event.VersionRetrieved(object, info))

        return object

    def getVersionIds(self, object):
        info = self.getVersionInfo(object)
        history = self.getVersionHistory(info.history_id)
        return history.getVersionIds()

    def getLabelsForResource(self, object):
        info = self.getVersionInfo(object)
        history = self.getVersionHistory(info.history_id)
        return history.getLabels()

    def getLogEntries(self, object):
        info = self.getVersionInfo(object)
        history = self.getVersionHistory(info.history_id)
        return history.getLogEntries()


def declare_versioned(object):
    """Apply bookkeeping needed to recognize an object version controlled."""
    ifaces = zope.interface.directlyProvidedBy(object)
    ifaces += IVersioned
    zope.interface.directlyProvides(object, *ifaces)
