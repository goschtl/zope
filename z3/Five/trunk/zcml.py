from zope.configuration import xmlconfig
import Products

_initialized = False
_global_context = None
def initialize(execute=True):
    """This gets called once to initialize ZCML enough.
    """
    global _initialized, _global_context
    if _initialized:
        return _global_context
    _global_context = xmlconfig.file('five.zcml', package=Products.Five)
    _initialized = True
    return _global_context

def reset():
    global _initialized, _global_context
    _initialized = False
    _global_context = None

def process(file, execute=True, package=None):
    """Process a ZCML file.

    Note that this can be called multiple times, unlike in Zope 3. This
    is needed because in Zope 2 we don't (yet) have a master ZCML file
    which can include all the others.
    """
    context = initialize()
    return xmlconfig.file(file, context=context, execute=execute,
                          package=package)

def string(s, execute=True):
    """Process a ZCML string.

    Note that this can be called multiple times, unlike in Zope 3. This
    is needed because in Zope 2 we don't (yet) have a master ZCML file
    which can include all the others.
    """
    context = initialize()
    return xmlconfig.string(s, context=context, execute=execute)
