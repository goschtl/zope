""" Simple, importable content classes.

$Id: faux_objects.py 40140 2005-11-15 18:53:19Z tseaver $
"""
from OFS.Folder import Folder
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem

from Products.CMFSetup.interfaces import IObjectManager
from Products.CMFSetup.interfaces import ISimpleItem
from Products.CMFSetup.interfaces import IPropertyManager

class TestSimpleItem(SimpleItem):
    __implements__ = (ISimpleItem, )

class TestSimpleItemWithProperties(SimpleItem, PropertyManager):
    __implements__ = (ISimpleItem, IPropertyManager)

KNOWN_CSV = """\
one,two,three
four,five,six
"""

from Products.CMFSetup.interfaces import ICSVAware
class TestCSVAware(SimpleItem):
    __implements__ = (ICSVAware, )
    _was_put = None
    _csv = KNOWN_CSV

    def as_csv(self):
        return self._csv

    def put_csv(self, text):
        self._was_put = text

KNOWN_INI = """\
[DEFAULT]
title = %s
description = %s
"""

from Products.CMFSetup.interfaces import IINIAware
class TestINIAware(SimpleItem):
    __implements__ = (IINIAware, )
    _was_put = None
    title = 'INI title'
    description = 'INI description'

    def as_ini(self):
        return KNOWN_INI % (self.title, self.description)

    def put_ini(self, text):
        self._was_put = text

KNOWN_DAV = """\
Title: %s
Description: %s

%s
"""

from Products.CMFSetup.interfaces import IDAVAware
class TestDAVAware(SimpleItem):
    __implements__ = (IDAVAware, )
    _was_put = None
    title = 'DAV title'
    description = 'DAV description'
    body = 'DAV body'

    def manage_FTPget(self):
        return KNOWN_DAV % (self.title, self.description, self.body)

    def PUT(self, REQUEST, RESPONSE):
        self._was_put = REQUEST.get('BODY', '')
        stream = REQUEST.get('BODYFILE', None)
        self._was_put_as_read = stream.read()
