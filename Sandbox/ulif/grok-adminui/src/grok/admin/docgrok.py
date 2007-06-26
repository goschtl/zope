"""The Grok's Friendly Doctor.

Ask DocGrok and he will try his best, to keep you well informed about
everything hanging around in your Zope3 and your Grok Application.
"""

import zope.component
from zope.app.folder.interfaces import IRootFolder
from zope.dottedname.resolve import resolve
from zope.interface.interface import InterfaceClass
from zope.security.proxy import isinstance
from zope.proxy import removeAllProxies

import os
import types
import grok
import inspect
import grok.interfaces
from martian.scan import is_package, ModuleInfo
from martian import InstanceGrokker, ModuleGrokker

from zope.app.i18n import ZopeMessageFactory as _

from zope.app.apidoc.codemodule.module import Module
from zope.app.apidoc.codemodule.class_ import Class

grok.context(IRootFolder)
grok.define_permission('grok.ManageApplications')



def handle_module( dotted_path, ob=None ):
    if ob is None:
        ob = resolve( dotted_path )
    if not hasattr(ob, '__file__'):
        return None
    if not is_package(os.path.dirname(ob.__file__)):
        return None
    if os.path.basename(ob.__file__) in ['__init__.py',
                                         '__init__.pyc',
                                         '__init__.pyo']:
        return None
    return DocGrokModule(dotted_path)

def handle_package( dotted_path, ob=None):
    if ob is None:
        ob = resolve( dotted_path )
    if not hasattr(ob, '__file__'):
        return None
    if not is_package(os.path.dirname(ob.__file__)):
        return None
    if os.path.basename(ob.__file__) not in ['__init__.py',
                                             '__init__.pyc',
                                             '__init__.pyo']:
        return None
    return DocGrokPackage(dotted_path)

def handle_interface(dotted_path, ob=None):
    if ob is None:
        ob = resolve(dotted_path)
    if not isinstance(
        removeAllProxies(ob), InterfaceClass):
        return None
    return DocGrokInterface(dotted_path)

def handle_class(dotted_path, ob=None):
    if ob is None:
        ob = resolve(dotted_path)
    if not isinstance(ob, (types.ClassType, type)):
        return None
    return DocGrokClass(dotted_path)

# The docgroks registry.
#
# We register 'manually', because the handlers
# are defined in the same module.
docgrok_handlers = [
    { 'name' : 'module',
      'handler' : handle_module },
    { 'name' : 'package',
      'handler' : handle_package },
    { 'name' : 'interface',
      'handler' : handle_interface },
    { 'name' : 'class',
      'handler' : handle_class } ]


def handle(dotted_path):
    """Find a doctor specialized for certain things.
    """
    try:
        ob = resolve( dotted_path )
    except ImportError:
        # There is no package of that name. Give back 404.
        # XXX Do something more intelligent, offer a search.
        return None
    except:
        return None

    for handler in docgrok_handlers:
        spec_handler = handler['handler']
        doc_grok = spec_handler( dotted_path, ob )
        if doc_grok is None:
            continue
        return doc_grok
    return DocGrok(dotted_path)

class DocGrokGrokker(InstanceGrokker):
    """A grokker that groks DocGroks.

    This grokker can help to 'plugin' different docgroks in an easy
    way. You can register docgroks for your special classes, modules,
    things. All required, is a function, that determines the correct
    kind of thing, you like to offer a docgrok for and returns a
    specialized docgrok or None (in case the thing examined is not the
    kind of thing your docgrok is a specialist for).

    Unfortunately, order counts here. If one docgrok handler is able
    to deliver a specialized docgrok object, no further invesitgation
    will be done.

    In principle, the following should work. First we import the
    docgrok module, because it contains a more specific grokker: the
    InstanceGrokker 'docgrok_grokker' ::

      >>> from grok.admin import docgrok

    Then we get create an (empty) 'ModuleGrokker'. 'ModuleGrokkers'
    can grok whole modules. ::
      
      >>> from martian import ModuleGrokker
      >>> module_grokker = ModuleGrokker()

    Then we register the 'docgrok_grokker', which should contain some
    base handlers for modules, classes, etc. by default::
      
      >>> module_grokker.register(docgrok.docgrok_grokker)

    The 'docgrok_grokker' is an instance of 'DocGrokGrokker'::

      >>> from grok.admin.docgrok import DocGrokGrokker
      >>> isinstance(docgrok.docgrok_grokker, DocGrokGrokker)
      True

    Now imagine, you have your own DocGroks for special things, for
    example for a class 'Mammoth'. You might have derived this class
    from DocGrok (or a subclass thereof), but this is not a
    requirement. Note however, that other programmers might expect
    your DocGroks to be compatible in a certain manner, so it surely
    is a good idea to derive your GrokDocs from the original one.

    Let's assume, your DocGrokMammoth is defined in a module called
    'mammoth'::

      >>> from grok.admin.docgrok import DocGrok
      >>> class mammoth(FakeModule):
      ...   class Mammoth(object):
      ...     pass
      ...
      ...   class MammothDocGrok(DocGrok):
      ...     def isMammoth(self):
      ...       return True
      ...
      ...   def handle_mammoths(dotted_path,ob=None):
      ...     if not isinstance(ob, Mammoth):
      ...       return None
      ...     return MammothDocGrok(dotted_path)

    This is a simple DocGrok ('MammothDocGrok') accompanied by a
    thing, it is representing (class 'Mammoth') and a handler
    function, which decides, whether a given dotted path denotes a
    Mammoth or not. The FakeModule class is a workaround to emulate
    modules in doctests. Just think of watching a module, when you see
    a FakeModule class.

    Now we want to register this new DocGrok with the 'global
    machinery'. Easy::
    
      >>> module_grokker.grok( 'mammoth_grokker', mammoth )
      True
      
    Now the 'handle_mammoths' function is considered to deliver a
    valid DocGrok, whenever it is asked. Every time, someone asks the
    docgroks 'handle()' function for a suitable docgrok for things
    that happen to be Mammoths, a DocGrokMammoth will be served.

    Even the default docgrok viewer that comes with the grok package
    in the admin interface, now will deliver your special views for
    mammoths (if you defined one; otherwise the default 'DocGrok'
    template will be used to show mammoth information).

    XXX TODO: Show how to make a docgrok view.

    That's it.
    
    """
    component_class = types.FunctionType

    def grok(self, name, obj, **kw):        
        if not name.startswith('handle_'):
            return False
        if name in [x['name'] for x in docgrok_handlers]:
            return False
        #docgrok_handlers[name] = obj
        docgrok_handlers.insert( 0, {'name':name,
                                     'handler':obj})
        return True


## XXX deprecated...
def getThingsType( dotted_path ):
    """Determine type of thing described by a dotted path.

    None for: thing does not exist/is not accessible by resolve().

    'package' for: python package.
    
    'unknown' for: exists, but no special doctor for this desease.
    """
    try:
        ob = resolve( dotted_path )
    except ImportError:
        # There is no package of that name. Give back 404.
        # XXX Do something more intelligent, offer a search.
        return None
    except:
        return None

    if hasattr( ob, "__file__" ) and is_package(os.path.dirname(ob.__file__)):
        if os.path.basename(ob.__file__) in ['__init__.py',
                                             '__init__.pyc']:
            return "package"
        return "module"
    elif isinstance(removeAllProxies(ob), InterfaceClass):
        return "interface"
    elif inspect.isclass(ob):
        return "class"
    return "unknown"


def getDocGrokForDottedPath_obsolete( dotted_path ):
    """Find a doctor, which is a specialist for the dotted path element.
    """
    return handle(dotted_path)
    newtype = getThingsType( dotted_path )
    if newtype is None:
        # There is nothing of that name. Give back 404.
        # XXX Do something more intelligent, offer a search.
        return None
    elif newtype == "package":
        # We found a package. Let a DocGrokPackage handle further
        # things.
        doctor = DocGrokPackage( dotted_path )
    elif newtype == "module":
        doctor = DocGrokModule(dotted_path)
    elif newtype == "interface":
        doctor = DocGrokInterface(dotted_path)
    elif newtype == "class":
        doctor = DocGrokClass(dotted_path)
    else:
        doctor = DocGrok( dotted_path ) # Default
    return doctor
    
    
class DocGrok(grok.Model):
    """DocGrok helps us finding out things about ourselves.

    There are DocGroks for packages, modules, interfaces, etc., each
    one a specialist for a certain type of element. 'Pure' DocGroks
    build the root of this specialist hierarchy and care for objects,
    which can not be handled by other, more specialized DocGroks.

    DocGrok offers a minimum of information but can easily be extended in
    derived classes.
    """
    msg = "I am Dr. Grok. How can I help you?"
    path = None
    _traversal_root = None
    #_children = {}

    def __init__(self, dotted_path ):
        #super( DocGrok, self ).__init__()
        self.path = dotted_path

    def getPath(self):
        return self.path

    def getMsg(self):
        return self.msg

    def getFilePath( self ):
        ob = resolve( self.path )
        return hasattr(ob, __file__) and os.path.dirname(ob.__file__) or None

    def traverse(self,patient):
        """ Do special traversing inside the surgery.

        Inside the docgrok-'namespace' we only accept DocGroks and
        colleagues. Each DocGrok cares for a patient represented by a
        path. This path might denote an object in the ZODB or in the
        python path.

        """
        if patient == "index.html":
            return self
        if self.path is None:
            newpath = patient
        else:
            newpath = '.'.join([self.path, patient])

        #doctor = getDocGrokForDottedPath( newpath )
        doctor = handle( newpath )

        if doctor is None:
            # There is nothing of that name. Give back 404.
            # XXX Do something more intelligent, offer a search.
            return None
        #doctor.msg = "Do more grokking!"
        doctor.__parent__ = self
        doctor.__name__ = patient
        doctor._traversal_root = self._traversal_root
        doctor.path = newpath
        return doctor
    pass

class DocGrokTraverser(grok.Traverser):
    """If first URL element is 'docgrok', handle over to DocGrok.

    This traverser binds to the RootFolder, which means, it is only
    asked, when the publisher looks for elements in the Zope root (or
    another IRootFolder). The further traversing is done by the Docs'
    own traverser in it's model. See method `traverse()` in DocGrok.
    """
    grok.context(IRootFolder)

    def traverse(self,path):
        if path == "docgrok":
            doctor = DocGrok(None)
            # Giving a __parent__ and a __name__, we make things
            # locatable in sense of ILocatable.
            doctor.__parent__ = self.context
            doctor.__name__ = 'docgrok'
            doctor._traversal_root = doctor
            return doctor
        return None


class DocGrokPackage(DocGrok):
    """This doctor cares for python packages.
    """
    msg = "I am a Package of the Doc"
    path=None
    apidoc = None
    _traversal_root = None

    def __init__(self,dotted_path):
        self.path = dotted_path
        self._module = resolve(self.path)
        # In apidoc packages are handled like modules...
        self.apidoc = Module( None, None, self._module, True)

    def getDocString( self ):
        return self.apidoc.getDocString()

    def getFilePath( self ):
        ob = resolve( self.path )
        return os.path.dirname( ob.__file__ ) + '/'

    def _getModuleInfos( self, filter_func=lambda x:x ):
        """Get modules and packages of a package.

        The filter function will be applied to a list of modules and
        packages of type grok.scan.ModuleInfo.
        """
        ob = resolve( self.path )
        filename = ob.__file__
        module_info = ModuleInfo( filename, self.path )
        infos = module_info.getSubModuleInfos()
        if filter_func is not None:
            infos = filter( filter_func, infos)
        #infos = [x for x in infos if not x.isPackage()]
        result = []
        for info in infos:
            subresult = {}
            # Build a url string from dotted path...
            mod_path = "docgrok"
            for path_part in info.dotted_name.split('.'):
                mod_path = os.path.join( mod_path, path_part )
            subresult = {
                'url' : mod_path,
                'name' : info.name,
                'dotted_name' : info.dotted_name
                }
            result.append( subresult )
        return result
        

    def getModuleInfos( self ):
        """Get the modules inside a package.
        """
        filter_func = lambda x: not x.isPackage()
        return self._getModuleInfos( filter_func )

    def getSubPackageInfos( self ):
        """Get the subpackages inside a package.
        """
        filter_func = lambda x: x.isPackage()
        return self._getModuleInfos( filter_func )

    def getChildren( self ):
        result = self.apidoc.items()
        result.sort( lambda x,y:cmp(x[0], y[0]) )
        return result


class DocGrokModule(DocGrokPackage):
    """This doctor cares for python modules.
    """

    def getFilePath( self ):
        ob = resolve( self.path )
        filename = ob.__file__
        if filename.endswith('o') or filename.endswith('c'):
            filename = filename[:-1]
        return filename

       
class DocGrokClass(DocGrokPackage):
    """This doctor cares for classes.
    """
    def __init__(self,dotted_path):
        self.path = dotted_path
        self.klass = resolve(self.path)
        self.module_path, self.name = dotted_path.rsplit('.',1)
        self.module = resolve( self.module_path )
        mod_apidoc = Module( None, None, self.module, False)
        self.apidoc = Class( mod_apidoc, self.name, self.klass)

    def getFilePath( self ):
        if not hasattr( self.module, "__file__" ):
            return None
        filename = self.module.__file__
        if filename.endswith('o') or filename.endswith('c'):
            filename = filename[:-1]
        return filename

class DocGrokInterface(DocGrokClass):
    """This doctor cares for interfaces.
    """
    def __init__(self,dotted_path):
        self.path = dotted_path
        self.klass = resolve(self.path)
        self.module_path, self.name = dotted_path.rsplit('.',1)
        self.module = resolve( self.module_path )
        mod_apidoc = Module( None, None, self.module, False)
        self.apidoc = Class( mod_apidoc, self.name, self.klass)

    def getFilePath( self ):
        if not hasattr( self.module, "__file__" ):
            return None
        filename = self.module.__file__
        if filename.endswith('o') or filename.endswith('c'):
            filename = filename[:-1]
        return filename
