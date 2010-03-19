"""Components representing the Python namespace root.
"""
import pkg_resources
import grokcore.view as grok
from martian.scan import module_info_from_dotted_name
from zope.introspector.code import Code, Package, Module
from zope.introspector.interfaces import IInfo
from zope.location import LocationProxy

grok.templatedir('templates')

class NamespaceRoot(Code):
    def __init__(self, dotted_name=''):
        self.dotted_name = ''
        
    def __getitem__(self, name):
        sub_module = None
        try:
            sub_module = module_info_from_dotted_name(name)
        except ImportError:
            # No module of that name found. The name might denote
            # something different like a file or be really trash.
            pass
        if sub_module is None:
            raise KeyError
        if sub_module.isPackage():
            return Package(sub_module.dotted_name)
        return Module(sub_module.dotted_name)

class NamespaceRootInfo(grok.Adapter):
    grok.context(NamespaceRoot)
    grok.provides(IInfo)
    grok.name('coderoot')
    
    def getDottedName(self):
        return self.context.dotted_name

    def getSubItems(self):
        importables = pkg_resources.Environment()
        top_level_pkgs = [x.split('.')[0] for x in importables]
        top_level_pkgs = sorted(list(set(top_level_pkgs)))
        for pkg in top_level_pkgs:
            yield pkg

    def _filterSubItems(self, filter=lambda x: True):
        for name in self.getSubItems():
            try:
                info = module_info_from_dotted_name(name)
                if filter and filter(info):
                    yield info
            except ImportError:
                pass
            except AttributeError:
                # This is thrown sometimes by martian.scan if an
                # object lacks a __file__ attribute and needs further
                # investigation.
                pass
        
    def getSubPackages(self):
        return sorted(self._filterSubItems(lambda x: x.isPackage()),
                      key=lambda x:x.dotted_name)

    def getModules(self):
        return sorted(self._filterSubItems(lambda x: not x.isPackage()))

class NamespaceRootInfoView(grok.View):
    grok.context(NamespaceRootInfo)
    grok.require('grok.BrowseCode')
    grok.name('index')
    grok.template('rootinfo')

    def item_url(self, info):
        return self.url(LocationProxy(info, self.context, info.dotted_name))
