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
"""Browser View Components for Bugs

$Id: bug.py,v 1.14 2004/03/18 18:04:54 philikon Exp $
"""
import docutils.core
import re

from zope.component.interfaces import IViewFactory
from zope.security.interfaces import Unauthorized, ForbiddenAttribute
from zope.interface import implements
from zope.proxy import removeAllProxies
from zope.schema.vocabulary import getVocabularyRegistry
from zope.security.checker import getChecker
from zope.structuredtext.html import HTML

from zope.app import zapi
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import TextWidget, TextAreaWidget, DropdownWidget
from zope.app.size.interfaces import ISized
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from bugtracker.interfaces import IComment
from bugtracker.interfaces import IBugDependencies
from bugtracker.browser.comment import CommentViewBase


class BugBaseView(object):
    """Get's all the fancy expressions for the attribute values."""

    def getCreated(self):
        dc = IZopeDublinCore(self.context)
        formatter = self.request.locale.dates.getFormatter('dateTime', 'short')
        return formatter.format(dc.created)

    created = property(getCreated)

    def getModified(self):
        dc = IZopeDublinCore(self.context)
        formatter = self.request.locale.dates.getFormatter('dateTime', 'short')
        if dc.modified is None:
            return self.created()
        return formatter.format(dc.modified)

    modified = property(getModified)

    def getSubmitter(self):
        registry = getVocabularyRegistry()
        users = registry.get(self.context, 'Users')
        id = self.context.submitter
        try:
            return users.getTerm(id).principal
        except LookupError:
            # There is no principal for this id, so let's just fake one.
            return {'id': id, 'login': id, 'title': id, 'description': id}

    submitter = property(getSubmitter)

    def getDescription(self):
        ttype = getattr(self.context.description, 'ttype', None)
        if ttype is not None:
            source = zapi.createObject(self.context.description.ttype,
                                       self.context.description)
            view = zapi.getMultiAdapter(
                (removeAllProxies(source), self.request))
            html = view.render()
        else:
            html = self.context.description
        return html

    description = property(getDescription)

    def getStatus(self):
        registry = getVocabularyRegistry()
        types = registry.get(zapi.getParent(self.context), 'Stati')
        return types.getTerm(self.context.status)

    status = property(getStatus)

    def getType(self):        
        registry = getVocabularyRegistry()
        types = registry.get(zapi.getParent(self.context), 'BugTypes')
        return types.getTerm(self.context.type)

    type = property(getType)

    def getRelease(self):
        if self.context.release is None:
            return u'not specified'
        registry = getVocabularyRegistry()
        types = registry.get(zapi.getParent(self.context), 'Releases')
        return types.getTerm(self.context.release)

    release = property(getRelease)

    def getPriority(self):
        registry = getVocabularyRegistry()
        types = registry.get(zapi.getParent(self.context), 'Priorities')
        return types.getTerm(self.context.priority)

    priority = property(getPriority)

    def getOwners(self):
        registry = getVocabularyRegistry()
        vocab = registry.get(self.context, 'Users')
        userTerms = []
        for id in self.context.owners:
            try:
                userTerms.append(vocab.getTerm(id).principal)
            except LookupError:
                # There is no principal for this id, so let's just fake one.
                userTerms.append(
                    {'id': id, 'login': id, 'title': id, 'description': id})
        return userTerms

    owners = property(getOwners)


# Make a custom widget for the vocabulary, so that default values are
# retrieved from the vocabulary and not the field.
class ManagableVocabularyWidget(DropdownWidget):

    def _getDefault(self):
        # Return the default value for this widget;
        # may be overridden by subclasses.
        return self.vocabulary.default.value
    

class AddBug(object):

    def nextURL(self):
        return '../'+self.context.contentName


class AddDependentBug(object):
    """Add a bug that is """

    def __init__(self, context, request):
        super(AddDependentBug, self).__init__(context, request)
        self.dependent = context.context
        context.context = zapi.getParent(self.dependent)
        self.label = "Add Bug (Dependent: %s)" %self.dependent.title

    def add(self, content):
        content = super(AddDependentBug, self).add(content)
        deps = IBugDependencies(self.dependent)
        deps.dependencies += (self.context.contentName,)
        return content

    def nextURL(self):
        return '../overview.html'


class EditBug(BugBaseView):

    def update(self):
        status = super(EditBug, self).update()
        if status.startswith('Updated'):
            return self.request.response.redirect('./@@overview.html')
        return status


class Overview(BugBaseView):
    """View class providing necessary methods for the bug overview."""

    def comments(self):
        """Get a list of all comments."""
        comments = []
        for name, obj in self.context.items():
            if IComment.providedBy(obj):
                comments.append(CommentViewBase(obj, self.request))
        return comments

    def attachments(self):
        """Get a list of all attachments."""
        attchs = []
        for name, obj in self.context.items():
            if not IComment.providedBy(obj):
                size = ISized(obj)
                attchs.append({'name': name, 'size': size.sizeForDisplay()})
        return attchs
        
    def dependencies(self):
        deps = IBugDependencies(self.context)
        return deps.dependencies


class Dependencies(object):

    def __init__(self, context, request):
        super(Dependencies, self).__init__(context, request)
        # For efficiency get these values once and be done.
        deps = IBugDependencies(self.context)
        # If the two conditions are not fulfilled, we are not going to need
        # the values.
        if self.canChangeDependencies() and self.getShowDepsOptions():
            self.dependencies = deps.dependencies
            self.dependents = deps.dependents    

    def dependencyValues(self):
        deps = IBugDependencies(self.context)
        dep_type = self.request.get('dep_type', 'dependencies')
        if dep_type == 'dependencies':
            return self.dependencies
        else:
            return self.dependents            

    def availableBugs(self):
        tracker = zapi.getParent(self.context)
        bugs = []
        for name, bug in tracker.items():
            # Make sure we do not list the bug itself
            if name != zapi.name(self.context):
                bugs.append({'name': name, 'title': bug.title})
        return bugs

    def setDependencyValues(self):
        dep_type = self.request.get('dep_type', 'dependencies')
        deps = IBugDependencies(self.context)

        if 'ADD' in self.request and 'add_deps' in self.request:
            if dep_type == 'dependencies':
                deps.addDependencies(tuple(self.request['add_deps']))
            else:
                deps.addDependents(tuple(self.request['add_deps']))

        if 'DELETE' in self.request and 'del_deps' in self.request:
            if dep_type == 'dependencies':
                deps.deleteDependencies(tuple(self.request['del_deps']))
            else:
                deps.deleteDependents(tuple(self.request['del_deps']))

        self.setShowDepsOptions()
        self.setDepType()

        return self.request.response.redirect(
            './@@dependencies.html?dep_type=' + dep_type)

    def _branchHTML(self, children):
        html = '<ul>\n'
        for child, subs in children:
            html += DependencyEntry(child, self.request)()
            if subs:
                html += self._branchHTML(subs)
        html += '</ul>\n'
        return html

    def branch(self):
        deps = IBugDependencies(self.context)
        children = deps.findChildren()
        return self._branchHTML(children)

    def _getAllSubs(self, children):
        all = map(lambda c: c[0], children)
        for child, subs in children:
            all += self._getAllSubs(subs)
        return all

    def getStatistics(self):
        deps = IBugDependencies(self.context)
        children = deps.findChildren()
        all = self._getAllSubs(children)
        all_num = len(all)
        if not all_num:
            return {}
        closed = len(filter(lambda b: b.status in ('closed', 'deferred'), all))
        new = len(filter(lambda b: b.status == 'new', all))
        open = len(filter(lambda b: b.status in ('open', 'assigned'), all))
        stats = {'total': all_num,
                 'closed': closed,
                 'closed_perc': '%.2f%%' %(closed*100.0/all_num),
                 'new': new,
                 'new_perc': '%.2f%%' %(new*100.0/all_num),
                 'open': open,
                 'open_perc': '%.2f%%' %(open*100.0/all_num),
                 }
        return stats

    def getDepType(self):
        return self.request.cookies.get('dep_type', 'dependencies')

    def setDepType(self):
        value = self.request.get('dep_type', 'dependencies')
        self.request.response.setCookie('dep_type', value)

    def getShowDepsOptions(self):
        return int(self.request.cookies.get('show_deps_options', '1'))

    def setShowDepsOptions(self):
        if 'COLLAPSE' in self.request:
            value = '0'
        else:
            value = '1'
        self.request.response.setCookie('show_deps_options', value)

    def canChangeDependencies(self):
        deps = IBugDependencies(self.context)
        checker = getChecker(deps)
        try:
            checker.check_setattr(deps, 'dependencies')
        except (Unauthorized, ForbiddenAttribute):
            return False
        return True
    
    legend = ViewPageTemplateFile('legend.pt')


class DependencyEntry(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def name(self):
        return zapi.name(self.context)

    __call__ = ViewPageTemplateFile('branchentry.pt')
