import martian
import megrok.resource as mr
import grokcore.component as grok
import grokcore.view
import grokcore.security

from hurry.resource import ResourceInclusion

from megrok.resource.directive import default_library_name, default_list
from zope.publisher.interfaces.browser import (IDefaultBrowserLayer,
                                               IBrowserRequest)

class LibraryGrokker(martian.ClassGrokker):
    martian.component(mr.Library)
    martian.directive(grok.name, get_default=default_library_name)
    martian.directive(mr.inclusion, get_default=default_list)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.security.require, name='permission')


    def execute(self, class_, config, name, inclusion, layer, permission, **kw):
        setattr(class_, 'name', name)
        for name, file, depends, bottom in inclusion:
            RI = ResourceInclusion(class_, file, depends=depends, bottom=bottom)
            setattr(class_, name, RI)
            class_.libs.append(name)
        return True    
