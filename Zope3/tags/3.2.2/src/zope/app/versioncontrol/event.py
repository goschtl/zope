"""Events for version control.

"""
__docformat__ = "reStructuredText"

import zope.interface

import zope.app.event.objectevent
import zope.app.versioncontrol.interfaces


class VersionEvent(zope.app.event.objectevent.ObjectEvent):

    def __init__(self, object, info):
        super(VersionEvent, self).__init__(object)
        self.info = info


class VersionControlApplied(VersionEvent):

    zope.interface.implements(
        zope.app.versioncontrol.interfaces.IVersionControlApplied)

    def __init__(self, object, info, message):
        super(VersionControlApplied, self).__init__(object, info)
        self.message = message

    def __str__(self):
        s = "applied version control to %s" % self.object
        if self.message:
            s = "%s:\n%s" % (s, self.message)
        return s


class VersionCheckedOut(VersionEvent):

    zope.interface.implements(
        zope.app.versioncontrol.interfaces.IVersionCheckedOut)

    def __str__(self):
        return "checked out %s, version %s" % (
            self.object, self.info.version_id)


class VersionCheckedIn(VersionEvent):

    zope.interface.implements(
        zope.app.versioncontrol.interfaces.IVersionCheckedIn)

    def __init__(self, object, info, message):
        super(VersionCheckedIn, self).__init__(object, info)
        self.message = message

    def __str__(self):
        return "checked in %s, version %s" % (
            self.object, self.info.version_id)


class VersionReverted(VersionEvent):

    zope.interface.implements(
        zope.app.versioncontrol.interfaces.IVersionReverted)

    def __str__(self):
        return "reverted %s to version %s" % (
            self.object, self.info.version_id)


class VersionUpdated(VersionEvent):

    zope.interface.implements(
        zope.app.versioncontrol.interfaces.IVersionReverted)

    def __init__(self, object, info, old_version_id):
        super(VersionUpdated, self).__init__(object, info)
        self.old_version_id = old_version_id

    def __str__(self):
        return "updated %s from version %s to %s" % (
            self.object, self.old_version_id, self.info.version_id)


class VersionRetrieved(VersionEvent):

    zope.interface.implements(
        zope.app.versioncontrol.interfaces.IVersionRetrieved)

    def __str__(self):
        return "retrieved %s, version %s" % (
            self.object, self.info.version_id)


class VersionLabelled(VersionEvent):

    zope.interface.implements(
        zope.app.versioncontrol.interfaces.IVersionLabelled)

    def __init__(self, object, info, label):
        super(VersionLabelled, self).__init__(object, info)
        self.label = label

    def __str__(self):
        return "created label %s from version %s of %s" % (
            self.label, self.info.version_id, self.object)


class BranchCreated(VersionEvent):

    zope.interface.implements(
        zope.app.versioncontrol.interfaces.IVersionReverted)

    def __init__(self, object, info, branch_id):
        super(BranchCreated, self).__init__(object, info)
        self.branch_id = branch_id

    def __str__(self):
        return "created branch %s from version %s of %s" % (
            self.branch_id, self.info.version_id, self.object)
