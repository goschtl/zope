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
"""Persistent Principal Storage and Authentication Plugin Views

$Id$
"""
__docformat__ = "reStructuredText"


class PrincipalManagement(object):
    """ """

    def add(self, login, password):
        if len(self.context) >= 1:
            id = max(self.context.keys())+1
        else:
            id = 1
        self.context[id] = (login, password)
        self.request.response.redirect('@@editForm.html')

    def delete(self, ids):
        for id in ids:
            del self.context[int(id)]
        self.request.response.redirect('@@editForm.html')

    def list(self):
        return [{'id': id, 'login': principal[0]}
                for id, principal in self.context.items()]
