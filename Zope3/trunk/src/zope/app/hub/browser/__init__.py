##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Define view component for object hub.

$Id$
"""
from zope.exceptions import NotFoundError
from zope.app.hub.interfaces import IObjectHub
from zope.app.i18n import ZopeMessageIDFactory as _


class Control:
    __used_for__ = IObjectHub

    # XXX: Another dead chicken. Guys, this view could do soo much, like aehm,
    # display the cataloged objects with a nice filter function?

    def objects(self):
        """Returns a sequence of objects registered with the hub.

        Each item in the sequence is a map:

            path    - path to the object as stored in the hub
            id      - object id as stored in the hub
            status  - either 'Missing' or 'OK'
            ok      - True if statis 'OK', False otherwise

        Missing objects are those that cannot be accessed via the hub
        with a call to getObject (NotFoundError raised).
        """
        result = []
        hub = self.context
        for path, id in hub.iterRegistrations():
            try:
                hub.getObject(id)
                status = _("OK")
                ok = True
            except NotFoundError:
                status = _("Missing")
                ok = False
            result.append({'path':path, 'id':id, 'status':status, 'ok':ok})
        result.sort(lambda lhs, rhs: cmp(lhs['path'], rhs['path']))
        return result

