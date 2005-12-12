# this is a product which sets up a DirectoryView

from Products.CMFCore.DirectoryView import DirectoryView
from Products.CMFCore.tests.base.dummy import DummyFolder
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.DirectoryView import addDirectoryViews

def initialize(context):
    GLOBALS = globals()
    registerDirectory('skins', GLOBALS)
    obj = DummyFolder()
    dv = addDirectoryViews(obj, 'skins', GLOBALS)
