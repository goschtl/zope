import grokcore.component as grok
from grokcore.component.interfaces import IContext
import types
from martian.scan import module_info_from_dotted_name
from martian.util import isclass
from zope.interface import implements
from zope.introspector.interfaces import IInfo
import os

class Code(object):
    implements(IContext)

    def __init__(self, dotted_name):
        self.dotted_name = dotted_name

class PackageOrModule(Code):
    def __init__(self, dotted_name):
        super(PackageOrModule, self).__init__(dotted_name)
        self._module_info = module_info_from_dotted_name(dotted_name)
    
class Package(PackageOrModule):
    def getPath(self):
        return os.path.dirname(self._module_info.path)
    
    def __getitem__(self, name):
        sub_module = None
        try:
            sub_module = module_info_from_dotted_name(
                self._module_info.dotted_name + '.' + name)
        except ImportError:
            # No module of that name found. The name might denote
            # something different like a file or be really trash.
            pass
        if sub_module is None:
            file = File(self.dotted_name, name)
            # if the file exists, use it, otherwise it's a KeyError - no
            # file is here
            if file.exists():
                return file
            else:
                raise KeyError
        if sub_module.isPackage():
            return Package(sub_module.dotted_name)
        return Module(sub_module.dotted_name)

class PackageInfo(grok.Adapter):
    grok.context(Package)
    grok.provides(IInfo)
    grok.name('package')

    def getPackageFiles(self):
        pkg_file_path = self.context.getPath()
        return sorted([x for x in os.listdir(pkg_file_path)
               if os.path.isfile(os.path.join(pkg_file_path, x))
               and (x.endswith('.txt') or x.endswith('.rst'))])

class Module(PackageOrModule):
    def __getitem__(self, name):
        module = self._module_info.getModule()
        obj = getattr(module, name, None)
        if obj is None:
            raise KeyError
        sub_dotted_name = self.dotted_name + '.' + name
        if isclass(obj):
            return Class(sub_dotted_name)
        elif type(obj) is types.FunctionType:
            return Function(sub_dotted_name)
        else:
            return Instance(sub_dotted_name)

class File(Code):
    def __init__(self, dotted_name, name):
        super(File, self).__init__(dotted_name)
        self.name = name

    def exists(self):
        """Check whether the file is a file we want to consider."""
        module_info = module_info_from_dotted_name(self.dotted_name)
        path = module_info.getResourcePath(self.name)
        return (os.path.isfile(path) and
                (path.endswith('.rst') or path.endswith('.txt')))

class Class(Code):
    pass

class Function(Code):
    pass

class Instance(Code):
    pass
