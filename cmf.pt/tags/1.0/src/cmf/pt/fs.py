import re

# BBB for Zope 2.10
try:
    from App.class_init import InitializeClass
except ImportError:
    from Globals import InitializeClass

from Products.CMFCore.FSObject import FSObject
from Products.CMFCore import DirectoryView
from Products.CMFCore import permissions

from Products.CMFFormController.BaseControllerPageTemplate import \
     BaseControllerPageTemplate as BaseCPT
from Products.CMFFormController.FSControllerBase import FSControllerBase

from Shared.DC.Scripts.Script import Script
from Shared.DC.Scripts.Signature import FuncCode
from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from RestrictedPython import Utilities

from five.pt.pagetemplate import BaseTemplateFile


class FSPageTemplate(BaseTemplateFile, FSObject, Script):
    meta_type = 'Filesystem Page Template'
    
    security = ClassSecurityInfo()
    security.declareObjectProtected(permissions.View)

    _default_bindings = {'name_subpath': 'traverse_subpath'}

    func_defaults = None
    func_code = FuncCode((), 0)

    utility_builtins = Utilities.utility_builtins

    def __init__(self, id, filepath, fullname=None, properties=None):
        FSObject.__init__(self, id, filepath, fullname, properties)
        self.ZBindings_edit(self._default_bindings)

        # instantiate page template
        BaseTemplateFile.__init__(self, filepath)

    def _readFile(self, reparse):
        # templates are lazy
        if reparse:
            self.read()

    def __call__(self, *args, **kwargs):
        bound = self.bind(self)
        return bound(*args, **kwargs)

    def _exec(self, bound_names, *args, **kwargs):
        # execute the template in a new security context.
        security = getSecurityManager()
        bound_names['user'] = security.getUser()
        security.addContext(self)

        try:
            kwargs.update(bound_names)
            kwargs['extra_context'] = bound_names
            return self(*args, **kwargs)
        finally:
            security.removeContext(self)

class FSControllerPageTemplate(FSPageTemplate, FSControllerBase, BaseCPT):
    def __init__(self, id, filepath, fullname=None, properties=None):
        FSPageTemplate.__init__(self, id, filepath, fullname, properties)
        self.filepath = filepath

        self._read_action_metadata(self.getId(), filepath)
        self._read_validator_metadata(self.getId(), filepath)

    def _readFile(self, reparse):
        FSPageTemplate._readFile(self, reparse)
        self._readMetadata()

    def _updateFromFS(self):
        # workaround for Python 2.1 multiple inheritance lameness
        return self._baseUpdateFromFS()

    def _readMetadata(self):
        # workaround for Python 2.1 multiple inheritance lameness
        return self._baseReadMetadata()

    def __call__(self, *args, **kwargs):
        return self._call(FSPageTemplate.__call__, *args, **kwargs)

InitializeClass(FSPageTemplate)
InitializeClass(FSControllerPageTemplate)

DirectoryView.registerFileExtension('pt', FSPageTemplate)
DirectoryView.registerFileExtension('zpt', FSPageTemplate)
DirectoryView.registerFileExtension('html', FSPageTemplate)
DirectoryView.registerFileExtension('htm', FSPageTemplate)
DirectoryView.registerFileExtension('cpt', FSControllerPageTemplate)

DirectoryView.registerMetaType('Page Template', FSPageTemplate)
DirectoryView.registerMetaType('Controller Page Template', FSControllerPageTemplate)

# Patch the ignore list, so that our .py source files don't show up in skins
# folders
old_ignore = DirectoryView.ignore_re
new_ignore_re = re.compile(r'\.|(.*~$)|#|(.*\.(.?pt|htm.?)\.py$)')
DirectoryView.ignore_re = new_ignore_re
