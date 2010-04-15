##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import os

from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

_www = os.path.join(os.path.dirname(__file__), 'www')
html = os.path.join(os.path.dirname(__file__), 'html')
view = 'View'


class TestRecorder(SimpleItem):
    """
    Test recorder object for Zope 2. This primarily exists to provide for
    traversal to the .js and .html files that make up the test recorder.
    """
    
    security = ClassSecurityInfo()
    meta_type = 'Test Recorder'

    manage_options = (
        {'label':'Info', 'action': 'manage_main'},
        ) + SimpleItem.manage_options

    security.declareProtected(view, 'manage_main')
    manage_main = PageTemplateFile('main.pt', _www)

    def __init__(self, id, title=''):
        self.id = id
        self.title = title

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST):
        """ Redirect to resource page.
        """
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/index.html')

    dict = locals()
    for name in os.listdir(html):
        if name.endswith('.html') or name.endswith('.js'):
            security.declareProtected(view, name)
            dict[name] = PageTemplateFile(name, html)


InitializeClass(TestRecorder)


addform = PageTemplateFile('addform.pt', _www)

def add(self, id, title='', RESPONSE=None):
    """add method"""
    obj = TestRecorder(id, title)
    self._setObject(id, obj)
    if RESPONSE is not None:
        RESPONSE.redirect(self.absolute_url()+'/manage_main')
