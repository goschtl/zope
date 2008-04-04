##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""

$Id$
"""
from zope.component import queryMultiAdapter
from z3ext.preferences.interfaces import IPreferenceGroup, IRootPreferences


class Navigation(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.isRoot = IRootPreferences.providedBy(context)
        if self.isRoot:
            return

        path = []
        parent = context
        while IPreferenceGroup.providedBy(parent):
            path.insert(0, parent)
            parent = parent.__parent__

        self.root, path = path[0], path[1:]

        self.data = self._process(self.root, path)

    def _process(self, context, path, level=1):
        request = self.request

        if path:
            data = []
            items = getattr(context, 'items', ())
            if callable(items):
                items = items()

            for name, prefs in items:
                if not prefs.isAvailable():
                    continue

                info = {'name': name,
                        'title': prefs.__title__,
                        'icon': queryMultiAdapter(
                             (prefs, request), name='zmi_icon'),
                        'items': (),
                        'selected': False,
                        'prefs': prefs,
                        'level': level}

                if prefs.__id__ == path[0].__id__:
                    info['items'] = self._process(prefs, path[1:], level+1)

                if prefs.__id__ == self.context.__id__:
                    info['selected'] = True
                    info['items'] = self._process(prefs, [prefs], level+1)

                data.append(info)

            return data

    def __call__(self):
        if self.isRoot:
            return ''
        else:
            return self.index()
