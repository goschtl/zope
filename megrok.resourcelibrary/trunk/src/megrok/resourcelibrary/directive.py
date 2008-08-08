import os

import martian
from martian import util
from martian.error import GrokImportError

from zc.resourcelibrary.zcml import INCLUDABLE_EXTENTIONS

def default_list(factory, module=None, **data):
    return []

def default_library_name(factory, module=None, **data):
    return factory.__name__.lower()

class directory(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE

    validate = martian.validateText
    
class depend(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE
    validate = martian.validateClass
    
class include(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE
    
    def validate(self, value):
        if util.not_unicode_or_ascii(value):
            raise GrokImportError(
                "You can only pass unicode or ASCII to the '%s' directive." %
                self.name)
        ext = os.path.splitext(value)[1]
        if ext not in INCLUDABLE_EXTENTIONS:
            raise GrokImportError(
                "The '%s' directive does not know how to include this file: %s" %
                (value, self.name))

