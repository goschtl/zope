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

from ZTUtils import make_query

class ZMIView(object):
    """ ZMI base view
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request


    def redirect(self, url, status=''):
        """ Redirect to a url and provide an optional status message
        """
        if status:
            url = '%s%s' % (url, make_query(zmi_status=status))
        self.request.response.redirect(url)

