##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
__docformat__ = "reStructuredText"

import os
import tempfile

# set the extfile directory for testing to a temprary directory
extfileDir = tempfile.mkdtemp()
os.environ['EXTFILE_STORAGEDIR'] = tempfile.mkdtemp()

class In2OutApplication(object):
    """
    returns the input stream
    """
    def __call__(self, environ, start_response):
        #import pdb;pdb.set_trace()
        start_response("200 OK", [('Content-Type', 'text/plain')])
        for l in environ.get('wsgi.input'):
            yield l

def app_factory(global_conf, **local_conf):
    return In2OutApplication()
