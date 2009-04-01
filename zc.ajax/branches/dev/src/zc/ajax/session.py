##############################################################################
#
# Copyright (c) Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import simplejson
import zope.app.exception.browser.unauthorized

class Unauthorized(zope.app.exception.browser.unauthorized.Unauthorized):

    def __call__(self):
        if (self.request.getHeader('X-Requested-With', '').lower()
            == 'xmlhttprequest'):
            return simplejson.dumps(
                dict(success=False, session_expired = True)
                )
        return zope.app.exception.browser.unauthorized.Unauthorized.__call__(
            self)
