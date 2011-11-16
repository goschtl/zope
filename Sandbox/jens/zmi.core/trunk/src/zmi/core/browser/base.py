##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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
""" Base view for ZMI views
"""

from zope import i18n # disambiguation
from zope.i18nmessageid import MessageFactory
from ZTUtils import make_query

Message = MessageFactory('zmi.core')

def translate(message, request):
    """ Translate i18n message.
    """
    if isinstance(message, Exception):
        try:
            message = message[0]
        except (TypeError, IndexError):
            pass
    return i18n.translate(message, domain='zmi.core', context=request)


class ZMIView(object):
    """ ZMI base view
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.status = None

    def redirect(self, target=None, keys=''):
        """ Redirect to a url and provide an optional status message
        """
        if target is None:
            target = self.request.ACTUAL_URL

        kw = {}
        if self.status:
            message = translate(self.status, self.context)
            if isinstance(message, unicode):
                message = message.encode('utf-8')
            kw['manage_tabs_message'] = message
        for k in keys.split(','):
            k = k.strip()
            v = self.request.form.get(k, None)
            if v:
                kw[k] = v

        query = kw and ('?%s' % make_query(kw)) or ''
        self.request.response.redirect('%s%s' % (target, query))

        return ''
