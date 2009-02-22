##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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

from zope.component import queryMultiAdapter
from zope.publisher.interfaces import IResult

from zope.pipeline.envkeys import STRING_RESULT_HOOKS_KEY

class Response:

    def setResult(self, result):
        if IResult.providedBy(result):
            r = result
        else:
            r = queryMultiAdapter((result, self._request), IResult)
            if r is None:
                if isinstance(result, basestring):
                    r = result
                elif result is None:
                    r = ''
                else:
                    raise TypeError(
                        'The result should be None, a string, or adaptable to '
                        'IResult.')
            if isinstance(r, basestring):
                environ = self._request.environment
                hooks = environ.get(STRING_RESULT_HOOKS_KEY)
                if hooks:
                    for hook in hooks:
                        r = hook(r, environ)
                r = (r,)

        self._result = r
        if not self._status_set:
            self.setStatus('Ok')
