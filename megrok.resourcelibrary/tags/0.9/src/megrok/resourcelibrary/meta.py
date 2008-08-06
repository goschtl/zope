import os

import martian
import grok
from martian.error import GrokError

from zope.publisher.interfaces.browser import (IDefaultBrowserLayer,
                                               IBrowserRequest)
from zope.app.publisher.browser import directoryresource
from zope.app.publisher.browser.resourcemeta import allowed_names
from zope.security.checker import CheckerPublic, NamesChecker
from zc.resourcelibrary.zcml import handler
from zc.resourcelibrary.resourcelibrary import LibraryInfo, library_info
from zope.interface import Interface

from megrok import resourcelibrary
from megrok.resourcelibrary.directive import default_list, default_library_name

class ResourceLibraryGrokker(martian.ClassGrokker):
    martian.component(resourcelibrary.ResourceLibrary)
    martian.directive(grok.name, get_default=default_library_name)
    martian.directive(resourcelibrary.directory)
    martian.directive(resourcelibrary.use, get_default=default_list)
    martian.directive(resourcelibrary.include, get_default=default_list)
    martian.directive(grok.layer, default=IDefaultBrowserLayer)
    martian.directive(grok.require, name='permission')
    
    def grok(self, name, factory, module_info, **kw):
        # need to tuck away module_info
        factory.module_info = module_info
        return super(ResourceLibraryGrokker, self).grok(
            name, factory, module_info, **kw)
    
    def execute(self, class_, config, name, directory, use, include, layer,
                permission,
                **kw):
        directory = class_.module_info.getResourcePath(directory)
        if not os.path.isdir(directory):
            raise GrokImportError(
                "You can only pass a directory to the '%s' directive." %
                self.name)

        library_info[name] = LibraryInfo()
        library_info[name].required.extend(use)
        library_info[name].included.extend(include)

        if permission == 'zope.Public' or permission is None:
            permission = CheckerPublic
        checker = NamesChecker(allowed_names, permission)

        factory = directoryresource.DirectoryResourceFactory
        factory = factory(directory, checker, name)
        
        config.action(
            discriminator=('resource', name, IBrowserRequest, layer),
            callable=handler,
            args=(name, library_info[name].required, (layer,),
                  Interface, name, factory, config.info),
            )
        return True
