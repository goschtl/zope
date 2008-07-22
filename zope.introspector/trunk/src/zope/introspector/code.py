from grokcore.component.interfaces import IContext
import types
from martian.scan import module_info_from_dotted_name
from martian.util import isclass
from zope.interface import implements

class Code(object):
    implements(IContext)

    def __init__(self, dotted_name):
        self.dotted_name = dotted_name

class PackageOrModule(Code):
    def __init__(self, dotted_name):
        super(PackageOrModule, self).__init__(dotted_name)
        self._module_info = module_info_from_dotted_name(dotted_name)
    
class Package(PackageOrModule):
    def __getitem__(self, name):
        sub_module = self._module_info.getSubModuleInfo(name)
        if sub_module is None:
            raise KeyError
        if sub_module.isPackage():
            return Package(sub_module.dotted_name)
        return Module(sub_module.dotted_name)

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

class Class(Code):
    pass

class Function(Code):
    pass

class Instance(Code):
    pass
