import os
from types import TupleType

from zope.interface import implements
from zope import component

from hurry.resource import interfaces

EXTENSIONS = ['.css', '.kss', '.js']

class Library(object):
    implements(interfaces.ILibrary)
    
    def __init__(self, name):
        self.name = name

class ResourceInclusion(object):
    """Resource inclusion
    
    A resource inclusion specifies how to include a single resource in
    a library.
    """
    implements(interfaces.IResourceInclusion)
    
    def __init__(self, library, relpath, depends=None, rollups=None, **kw):
        """Create a resource inclusion

        library - the library this resource is in
        relpath - the relative path from the root of the library indicating
                  the actual resource
        depends - optionally, a list of resources that this resource depends
                  on. Entries in the list can be
                  ResourceInclusions or strings indicating the path.
                  In case of a string, a ResourceInclusion assumed based
                  on the same library as this inclusion.
        rollups - optionally, a list of resources that this resource can
                  be rolled up into. Entries in the list can be
                  ResourceInclusions or strings indicating the path.
                  In case of a string, a ResourceInclusion assumed based
                  on the same library as this inclusion.
        keyword arguments - different paths that represent the same
                  resource in different modes (debug, minified, etc),
                  or alternatively a fully specified ResourceInclusion.
        """
        self.library = library
        self.relpath = relpath

        assert not isinstance(rollups, basestring)
        rollups = rollups or []
        self.rollups = normalize_inclusions(library, rollups)

        assert not isinstance(depends, basestring)
        depends = depends or []
        self.depends = normalize_inclusions(library, depends)

        normalized_modes = {}
        for mode_name, inclusion in kw.items():
            normalized_modes[mode_name] = normalize_inclusion(
                library, inclusion)
        self.modes = normalized_modes
        
    def __repr__(self):
        return "<ResourceInclusion '%s' in library '%s'>" % (
            self.relpath, self.library.name)

    def ext(self):
        name, ext = os.path.splitext(self.relpath)
        return ext

    def mode(self, mode):
        if mode is None:
            return self
        # try getting the alternative
        try:
            return self.modes[mode]
        except KeyError:
            # fall back on the default mode if mode not found
            return self
    
    def key(self):
        return self.library.name, self.relpath

    def need(self):
        needed = component.getUtility(
            interfaces.ICurrentNeededInclusions)()
        needed.need(self)

    def inclusions(self):
        """Get all inclusions needed by this inclusion, including itself.
        """
        result = []
        for depend in self.depends:
            result.extend(depend.inclusions())
        result.append(self)
        return result

def normalize_inclusions(library, inclusions):
    return [normalize_inclusion(library, inclusion)
            for inclusion in inclusions]

def normalize_inclusion(library, inclusion):
    if isinstance(inclusion, ResourceInclusion):
        return inclusion
    assert isinstance(inclusion, basestring)
    return ResourceInclusion(library, inclusion)

class NeededInclusions(object):
    def __init__(self):
        self._inclusions = []

    def need(self, inclusion):
        self._inclusions.append(inclusion)

    def _sorted_inclusions(self):
        return reversed(sorted(self._inclusions, key=lambda i: i.depth()))
    
    def inclusions(self, mode=None):
        inclusions = []
        for inclusion in self._inclusions:
            inclusions.extend(inclusion.inclusions())

        inclusions = apply_mode(inclusions, mode)
        inclusions = consolidate(inclusions)
        # sort only by extension, not dependency, as we can rely on
        # python's stable sort to keep inclusion order intact
        inclusions = sort_inclusions_by_extension(inclusions)
        inclusions = remove_duplicates(inclusions)
        return inclusions
            
    def render(self, mode=None):
        result = []
        get_inclusion_url = component.getUtility(interfaces.IInclusionUrl)
        for inclusion in self.inclusions(mode):
            url = get_inclusion_url(inclusion)
            result.append(render_inclusion(inclusion, url))
        return '\n'.join(result)

def apply_mode(inclusions, mode):
    return [inclusion.mode(mode) for inclusion in inclusions]

def remove_duplicates(inclusions):
    """Given a set of inclusions, consolidate them so each nly occurs once.
    """
    seen = set()
    result = []
    for inclusion in inclusions:
        if inclusion.key() in seen:
            continue
        seen.add(inclusion.key())
        result.append(inclusion)
    return result

def consolidate(inclusions):
    # first map rollup -> list of inclusions that are in this rollup
    rollup_to_inclusions = {}   
    for inclusion in inclusions:
        for rollup in inclusion.rollups:
            rollup_to_inclusions.setdefault(rollup.key(), []).append(
                inclusion)

    # now replace inclusion with rollup consolidated biggest amount of
    # inclusions, or keep inclusion if no such rollup exists
    result = []
    for inclusion in inclusions:
        potential_rollups = []
        for rollup in inclusion.rollups:
            potential_rollups.append((len(rollup_to_inclusions[rollup.key()]),
                                      rollup))
        if not potential_rollups:
            # no rollups at all
            result.append(inclusion)
            continue
        sorted_rollups = sorted(potential_rollups)
        amount, rollup = sorted_rollups[-1]
        if amount > 1:
            result.append(rollup)
        else:
            result.append(inclusion)
    return result

def sort_inclusions_by_extension(inclusions):

    def key(inclusion):
        return EXTENSIONS.index(inclusion.ext())

    return sorted(inclusions, key=key)

def sort_inclusions_topological(inclusions):
    """Sort inclusions by dependency.

    Note that this is not actually used in the system, but can be used
    to resort inclusions in case sorting order is lost - or if the
    assumptions in this library turn out to be incorrect.
    """
    dead = {}
    result = []
    for inclusion in inclusions:
        dead[inclusion.key()] = False

    for inclusion in inclusions:
        _visit(inclusion, result, dead)
    return result

def _visit(inclusion, result, dead):
    if dead[inclusion.key()]:
        return
    dead[inclusion.key()] = True
    for depend in inclusion.depends:
        _visit(depend, result, dead)
    result.append(inclusion)

def render_css(url):
    return ('<link rel="stylesheet" type="text/css" href="%s" />' %
            url)

def render_kss(url):
    raise NotImplementedError

def render_js(url):
    return ('<script type="text/javascript" src="%s"></script>' %
            url)

inclusion_renderers = {
    '.css': render_css,
    '.kss': render_kss,
    '.js': render_js,
    }

def render_inclusion(inclusion, url):
    renderer = inclusion_renderers.get(inclusion.ext(), None)
    if renderer is None:
        raise UnknownResourceExtension(
            "Unknown resource extension %s for resource inclusion: %s" %
            (inclusion.ext(), repr(inclusion)))
    return renderer(url)
