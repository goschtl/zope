import martian
import megrok.resource as mr
import grokcore.component as grok
import grokcore.view

from hurry.resource import ResourceInclusion
from megrok.resource.directive import default_library_name, default_list


class LibraryGrokker(martian.ClassGrokker):
    martian.component(mr.Library)
    martian.directive(grok.name, get_default=default_library_name)

    def execute(self, klass, config, name, **kw):
        klass.name = name
        return True    
