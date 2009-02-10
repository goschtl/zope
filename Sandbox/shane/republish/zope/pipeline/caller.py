
from zope.proxy import removeAllProxies

class Caller(object):
    """WSGI app that calls the traversed object.

    Requires 'zope.request', which implements IRequest, in the environment.
    """
    def __call__(self, environ, start_response):
        request = environ['zope.request']
        name, ob = request.traversed[-1]
        result = mapply(ob, request.getPositionalArguments(), request)
        response = request.response
        if result is not response:
            response.setResult(result)
        start_response(response.getStatusString(), response.getHeaders())
        return response.consumeBodyIter()


_marker = object()  # Create a new marker object.

def unwrapMethod(obj):
    """obj -> (unwrapped, wrapperCount)

    Unwrap 'obj' until we get to a real function, counting the number of
    unwrappings.

    Bail if we find a class or something we can't identify as callable.
    """
    wrapperCount = 0
    unwrapped = obj

    for i in range(10):
        bases = getattr(unwrapped, '__bases__', None)
        if bases is not None:
            raise TypeError("mapply() can not call class constructors")

        im_func = getattr(unwrapped, 'im_func', None)
        if im_func is not None:
            unwrapped = im_func
            wrapperCount += 1
        elif getattr(unwrapped, 'func_code', None) is not None:
            break
        else:
            unwrapped = getattr(unwrapped, '__call__' , None)
            if unwrapped is None:
                raise TypeError("mapply() can not call %s" % repr(obj))
    else:
        raise TypeError("couldn't find callable metadata, mapply() error on %s"
                        % repr(obj))

    return unwrapped, wrapperCount


def mapply(obj, positional=(), request={}):
    __traceback_info__ = obj

    # we need deep access for introspection. Waaa.
    unwrapped = removeAllProxies(obj)

    unwrapped, wrapperCount = unwrapMethod(unwrapped)

    code = unwrapped.func_code
    defaults = unwrapped.func_defaults
    names = code.co_varnames[wrapperCount:code.co_argcount]

    nargs = len(names)
    if not positional:
        args = []
    else:
        args = list(positional)
        if len(args) > nargs:
            given = len(args)
            if wrapperCount:
                given += wrapperCount
            raise TypeError('%s() takes at most %d argument%s(%d given)' % (
                getattr(unwrapped, '__name__', repr(obj)),
                code.co_argcount,
                (code.co_argcount > 1 and 's ' or ' '),
                given))

    get = request.get
    nrequired = len(names)
    if defaults:
        nrequired -= len(defaults)

    for index in range(len(args), nargs):
        name = names[index]
        v = get(name, _marker)
        if v is _marker:
            if name == 'REQUEST':
                v = request
            elif index < nrequired:
                raise TypeError('Missing argument to %s(): %s' % (
                    getattr(unwrapped, '__name__', repr(obj)), name))
            else:
                v = defaults[index - nrequired]
        args.append(v)

    args = tuple(args)

    if __debug__:
        return debug_call(obj, args)

    return obj(*args)

def debug_call(obj, args):
    # The presence of this function allows us to set a pdb breakpoint
    return obj(*args)
