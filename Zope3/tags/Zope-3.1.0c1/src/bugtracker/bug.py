##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""A Container based Bug

$Id: bug.py,v 1.4 2003/08/28 05:22:30 srichter Exp $
"""
from zope.interface import implements
from zope.proxy import removeAllProxies

from zope.app import zapi
from zope.app.annotation.interfaces import IAnnotations
from zope.app.container.btree import BTreeContainer
from zope.app.container.contained import contained
from zope.app.dublincore.interfaces import IZopeDublinCore

from bugtracker.interfaces import IBug, IComment
from bugtracker.interfaces import IAttachmentContainer
from bugtracker.interfaces import IBugDependencies
from bugtracker.interfaces import IBugTrackerContained
from bugtracker.interfaces import ISearchableText
from bugtracker.vocabulary import VocabularyPropertyGetter
from bugtracker.vocabulary import VocabularyPropertySetter
from bugtracker import TrackerMessageID as _

DependencyKey = 'bugtracker.dependencies'


class Bug(BTreeContainer):

    implements(IBug, IAttachmentContainer, IBugTrackerContained)

    # See zopeproducts.bugtracker.interfaces.IBug
    status = property(
        VocabularyPropertyGetter('_status', _('Stati')),
        VocabularyPropertySetter('_status', _('Stati')))

    # See zopeproducts.bugtracker.interfaces.IBug
    priority = property(
        VocabularyPropertyGetter('_priority', _('Priorities')),
        VocabularyPropertySetter('_priority', _('Priorities')))

    # See zopeproducts.bugtracker.interfaces.IBug
    type = property(
        VocabularyPropertyGetter('_type', _('BugTypes')),
        VocabularyPropertySetter('_type', _('BugTypes')))

    # See zopeproducts.bugtracker.interfaces.IBug
    release = property(
        VocabularyPropertyGetter('_release', _('Releases')),
        VocabularyPropertySetter('_release', _('Releases')))

    def getOwners(self):
        return getattr(self, '_owners', [])
    
    def setOwners(self, owners):
        self._owners = removeAllProxies(owners)

    # See zopeproducts.bugtracker.interfaces.IBug
    owners = property(getOwners, setOwners)

    def setTitle(self, title):
        """Set bug title."""
        dc = IZopeDublinCore(self)
        dc.title = title

    def getTitle(self):
        """Get bug title."""
        dc = IZopeDublinCore(self)
        return dc.title

    # See zopeproducts.bugtracker.interfaces.IBug
    title = property(getTitle, setTitle)

    def setDescription(self, description):
        """Set bug description."""
        dc = IZopeDublinCore(self)
        dc.description = description

    def getDescription(self):
        """Get bug description."""
        dc = IZopeDublinCore(self)
        return dc.description

    # See zopeproducts.bugtracker.interfaces.IBug
    description = property(getDescription, setDescription)    

    def getSubmitter(self):
        """Get bug submitter."""
        dc = IZopeDublinCore(self)
        if not dc.creators:
            return None
        return dc.creators[0]

    # See zopeproducts.bugtracker.interfaces.IBug
    submitter = property(getSubmitter)    


class BugDependencyAdapter(object):

    implements(IBugDependencies)
    __used_for__ = IBug

    def __init__(self, context):
        self.context = self.__parent__ = context
        self._annotations = IAnnotations(context)
        if not self._annotations.get(DependencyKey):
            self._annotations[DependencyKey] = ()

    def addDependencies(self, dependencies):
        self._annotations[DependencyKey] += tuple(dependencies)

    def deleteDependencies(self, dependencies):
        self.dependencies = filter(lambda d: d not in dependencies,
                                   self.dependencies)

    def setDependencies(self, dependencies):
        self._annotations[DependencyKey] = tuple(dependencies)

    def getDependencies(self):
        return self._annotations[DependencyKey]

    dependencies = property(getDependencies, setDependencies)

    def addDependents(self, dependents):
        tracker = zapi.getParent(self.context)
        bug_id = zapi.name(self.context)
        for id in dependents:
            deps = IBugDependencies(tracker[id])
            deps.dependencies += (bug_id,)

    def deleteDependents(self, dependents):
        tracker = zapi.getParent(self.context)
        bug_id = zapi.name(self.context)
        for id in dependents:
            deps = IBugDependencies(tracker[id])
            d = filter(lambda x: str(x) != str(bug_id), deps.dependencies)
            deps.dependencies = tuple(d)

    def setDependents(self, dependents):
        tracker = zapi.getParent(self.context)
        bug_id = zapi.name(self.context)
        for id, bug in tracker.items():
            deps = IBugDependencies(bug)
            if bug_id in deps.dependencies and id not in dependents:
                d = list(deps.dependencies)
                d.remove(bug_id)
                deps.dependencies += tuple(d)
            if bug_id not in deps.dependencies and id in dependents:
                deps.dependencies += (bug_id,)

    def getDependents(self):
        tracker = zapi.getParent(self.context)
        bug_id = zapi.name(self.context)
        dependents = []
        for id, bug in tracker.items():
            deps = IBugDependencies(bug)
            if bug_id in deps.dependencies:
                dependents.append(id)
        return dependents

    dependents = property(getDependents, setDependents)

    def findChildren(self, recursive=True, all=None):
        "See zopeproducts.bugtracker.interfaces.IBugDependencies"
        if all is None:
            all = []
        tracker = zapi.getParent(self.context)
        contextName = zapi.name(self.context)
        deps = IBugDependencies(self.context)
        children = []
        for bugName in deps.dependencies:
            # Circle detection; if the bugName was processed before, skip it
            if bugName in all:
                continue
            else:
                all.append(bugName)

            bug = tracker[bugName]
            if recursive is True:
                deps = IBugDependencies(bug)
                subs = deps.findChildren(all=all)
            else:
                subs = ()

            children.append((bug, subs))

        return tuple(children)

class SearchableText:
    """This adapter allows us to get all searchable text at once.""" 

    implements(ISearchableText)
    __used_for__ = IBug

    def __init__(self, context):
        self.context = context

    def getSearchableText(self):
        return [self.context.title, self.context.description]
