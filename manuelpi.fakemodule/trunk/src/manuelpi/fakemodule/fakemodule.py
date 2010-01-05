import manuel
import re
import sys
import new
import textwrap

FAKE_MODULE_START = re.compile(
        r'^\.\.\s*module-block::?\s*(?P<module_name>[a-zA-Z_]+\S*)',
        re.MULTILINE)
FAKE_MODULE_END = re.compile(r'(\n\Z|\n(?=\S))')
MODULE_NAME = "manueltest"
MODULE_NAMESPACE = MODULE_NAME + ".fake"

# To store our fake module's lines
class FakeModuleSnippet(object):
    def __init__(self, code, module_name):
        self.code = code
        self.module_name = module_name

def find_fakes(document):
    for region in document.find_regions(FAKE_MODULE_START, FAKE_MODULE_END):
        if region.parsed:
            continue

        module_name = region.start_match.group('module_name')
        # Sanitise indentation
        source = textwrap.dedent('\n'.join(region.source.splitlines()[1:]))
        source_location = '%s:%d' % (document.location, region.lineno)

        code = compile(source, source_location, 'exec')
        document.claim_region(region)
        region.parsed = FakeModuleSnippet(code, module_name)

def execute_into_module(region, document, doc_globs):
    if not isinstance(region.parsed, FakeModuleSnippet):
        return

    # build a suitable module
    module_name = region.parsed.module_name
    full_module_name = MODULE_NAMESPACE + "." + module_name
    module = new.module(full_module_name)
    module_name_parts = full_module_name.split('.')
    module.__file__ = '/' + '/'.join(module_name_parts)

    # Make the module also available through normal import
    if not MODULE_NAMESPACE in sys.modules:
        sys.modules[MODULE_NAME] = new.module(MODULE_NAME)
        sys.modules[MODULE_NAMESPACE] = new.module(MODULE_NAMESPACE)
        sys.modules[MODULE_NAME].fake = sys.modules[MODULE_NAMESPACE]

    # We want to be able to resolve items that are in the surrounding
    # doctest globs. To acheive this, we force all doctest globals into
    # builtins such that they are resolved after module-scoped objects.
    import __builtin__
    __builtin__.__dict__.update(doc_globs)

    try:
        exec region.parsed.code in module.__dict__
        module.__exception__ = None
    except Exception, e:
        module.__exception__ = e

    # When we exec code within the dictionary namespace as
    # above, the __module__ attributes of the objects created are set
    # to __builtin__. We know better than the interpreter in this case
    # and are able to set the defined namespace accordingly. We 
    # iterate through and change the relevant attributes:
    for name in dir(module):
        if name.startswith('__'):
            continue
        obj = getattr(module, name)
        try:
            obj = obj.im_func
        except: 
            pass
        __module__ = None
        try:
            __module__ = obj.__dict__.get('__module__')
        except AttributeError:
            try:
                __module__ = obj.__module__
            except AttributeError:
                pass
        if __module__ in (None, '__builtin__'):
            try:
                obj.__module__ = full_module_name
            except AttributeError:
                pass
        setattr(module, name, obj)

    # Provide correct globals for functions
    for name in dir(module):
        if name.startswith('__'):
            continue
        obj = getattr(module, name)
        try:
            code = obj.func_code
            new_func = new.function(code, module.__dict__, name)
            new_func.__module__ = module.__name__
            setattr(module, name, new_func)
        except AttributeError:
            pass

    # Make the module visible and usable in the rest of the doctest
    doc_globs[module_name] =  module

    sys.modules[full_module_name] = module
    setattr(sys.modules['manueltest.fake'], 
                        full_module_name.split('.')[-1],
                        module)

class Manuel(manuel.Manuel):
    def __init__(self):
        manuel.Manuel.__init__(self, [find_fakes], [execute_into_module])
