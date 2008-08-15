

################################################################
# Monkey patch for LP #257276
#
# This code is taken from the encodings module of Python 2.4.
# Note that this code is originally (C) CNRI and it is possibly not compatible
# with the ZPL and therefore should not live within svn.zope.org. However this
# checkin is blessed by Jim Fulton for now. The fix is no longer required with
# Python 2.5 and hopefully fixed in Python 2.4.6 release.
################################################################

# Written by Marc-Andre Lemburg (mal@lemburg.com).
# (c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

def search_function(encoding):

    # Cache lookup
    entry = _cache.get(encoding, _unknown)
    if entry is not _unknown:
        return entry

    # Import the module:
    #
    # First try to find an alias for the normalized encoding
    # name and lookup the module using the aliased name, then try to
    # lookup the module using the standard import scheme, i.e. first
    # try in the encodings package, then at top-level.
    #
    norm_encoding = normalize_encoding(encoding)
    aliased_encoding = _aliases.get(norm_encoding) or \
                       _aliases.get(norm_encoding.replace('.', '_'))
    if aliased_encoding is not None:
        modnames = [aliased_encoding,
                    norm_encoding]
    else:
        modnames = [norm_encoding]
    for modname in modnames:

        if not modname or '.' in modname:
            continue

        try:
            mod = __import__(modname,
                             globals(), locals(), _import_tail)
            if not mod.__name__.startswith('encodings.'):
                continue

        except ImportError:
            pass
        else:
            break
    else:
        mod = None

    try:
        getregentry = mod.getregentry
    except AttributeError:
        # Not a codec module
        mod = None

    if mod is None:
        # Cache misses
        _cache[encoding] = None
        return None

    # Now ask the module for the registry entry
    entry = tuple(getregentry())
    if len(entry) != 4:
        raise CodecRegistryError,\
              'module "%s" (%s) failed to register' % \
              (mod.__name__, mod.__file__)
    for obj in entry:
        if not callable(obj):
            raise CodecRegistryError,\
                  'incompatible codecs in module "%s" (%s)' % \
                  (mod.__name__, mod.__file__)

    # Cache the codec registry entry
    _cache[encoding] = entry

    # Register its aliases (without overwriting previously registered
    # aliases)
    try:
        codecaliases = mod.getaliases()
    except AttributeError:
        pass
    else:
        for alias in codecaliases:
            if not _aliases.has_key(alias):
                _aliases[alias] = modname

    # Return the registry entry
    return entry

import sys
import encodings
if sys.version_info[:2] == (2,3):
    encodings._aliases = encodings.aliases.aliases
encodings.search_function.func_code = search_function.func_code


################################################################
# Monkey patch for LP #257269
# raise SystemExit exploit in PythonScripts
################################################################

import new
from Products.PythonScripts.PythonScript import PythonScript, \
     PythonScriptTracebackSupplement

def _exec(self, bound_names, args, kw):
    """Call a Python Script

    Calling a Python Script is an actual function invocation.
    """
    # Retrieve the value from the cache.
    keyset = None
    if self.ZCacheable_isCachingEnabled():
        # Prepare a cache key.
        keyset = kw.copy()
        asgns = self.getBindingAssignments()
        name_context = asgns.getAssignedName('name_context', None)
        if name_context:
            keyset[name_context] = aq_parent(self).getPhysicalPath()
        name_subpath = asgns.getAssignedName('name_subpath', None)
        if name_subpath:
            keyset[name_subpath] = self._getTraverseSubpath()
        # Note: perhaps we should cache based on name_ns also.
        keyset['*'] = args
        result = self.ZCacheable_get(keywords=keyset, default=_marker)
        if result is not _marker:
            # Got a cached value.
            return result

    #__traceback_info__ = bound_names, args, kw, self.func_defaults

    ft = self._v_ft
    if ft is None:
        __traceback_supplement__ = (
            PythonScriptTracebackSupplement, self)
        raise RuntimeError, '%s %s has errors.' % (self.meta_type, self.id)

    fcode, g, fadefs = ft
    g = g.copy()
    if bound_names is not None:
        g.update(bound_names)
    g['__traceback_supplement__'] = (
        PythonScriptTracebackSupplement, self, -1)
    g['__file__'] = getattr(self, '_filepath', None) or self.get_filepath()
    f = new.function(fcode, g, None, fadefs)

    try:
        result = f(*args, **kw)
    except SystemExit:
        raise ValueError('SystemExit cannot be raised within a PythonScript')

    if keyset is not None:
        # Store the result in the cache.
        self.ZCacheable_set(result, keywords=keyset)
    return result


PythonScript._exec = _exec
