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

class ResourceSpec(object):
    """Resource specification

    A resource specification specifies a single resource in a library.
    """
    implements(interfaces.IResourceSpec)
    
    def __init__(self, library, relpath, part_of=None, **kw):
        """Create a resource specification

        library - the library this resource is in
        relpath - the relative path from the root of the library indicating
                  the actual resource
        part_of - optionally, a resource is also part of a larger
                  consolidated resource. This can be a list of paths to the
                  larger resource in the same library. A list entry can also
                  be a fully specified ResourceSpec.
        key word arguments - different paths that represent the same
                  resource in different modes (debug, minified, etc),
                  or alternatively a fully specified ResourceSpec.
        """
        self.library = library
        self.relpath = relpath

        assert not isinstance(part_of, basestring)
        part_of = part_of or []
        normalized_part_of = []
        for part in part_of:
            if isinstance(part, ResourceSpec):
                normalized_part_of.append(part)
            else:
                normalized_part_of.append(
                    ResourceSpec(self.library, part))
        self.part_of = normalized_part_of
        
        self.modes = kw
        
    def ext(self):
        name, ext = os.path.splitext(self.relpath)
        return ext

    def mode(self, mode):
        if mode is None:
            return self
        # try getting the alternative
        try:
            mode_info = self.modes[mode]
            if isinstance(mode_info, ResourceSpec):
                return mode_info
            return ResourceSpec(self.library, mode_info)
        except KeyError:
            # fall back on the default mode if mode not found
            return self
    
    def key(self):
        return self.library.name, self.relpath
    
    def __repr__(self):
        return "<Resource '%s' in library '%s'>" % (
            self.relpath, self.library.name)

class Inclusion(object):
    implements(interfaces.IInclusion)
    
    def __init__(self, resources, depends=None):
        """Create an inclusion

        resources - the list of resource specs that should be on the page
                    when this inclusion is used.
        depends - one or more inclusions that this inclusion depends on.
        """
        self._resources = r = {}
        for resource in resources:
            ext_resources = r.setdefault(resource.ext(), [])
            ext_resources.append(resource)
        self.depends = depends or []

    def depth(self):
        depth = 0
        for depend in self.depends:
            depend_depth = depend.depth()
            if depend_depth > depth:
                depth = depend_depth
        return depth + 1
        
    def resources_of_ext(self, ext):
        resources = []
        for depend in self.depends:
            resources.extend(depend.resources_of_ext(ext))
        resources.extend(self._resources.get(ext, []))
        return resources

    def need(self):
        needed = component.getUtility(
            interfaces.ICurrentNeededInclusions)()
        needed.need(self)

class NeededInclusions(object):
    def __init__(self):
        self._inclusions = []

    def need(self, inclusion):
        self._inclusions.append(inclusion)

    def _sorted_inclusions(self):
        return reversed(sorted(self._inclusions, key=lambda i: i.depth()))
    
    def resources(self, mode=None):
        resources_of_ext = {}
        for inclusion in self._sorted_inclusions():
            for ext in EXTENSIONS:
                r = resources_of_ext.setdefault(ext, [])
                r.extend(inclusion.resources_of_ext(ext))
        resources = []
        for ext in EXTENSIONS:
            resources.extend(resources_of_ext.get(ext, []))
        resources = apply_mode(resources, mode)
        return remove_duplicates(consolidate(resources))
            
    def render(self, mode=None):
        result = []
        get_resource_url = component.getUtility(interfaces.IResourceUrl)
        for resource in self.resources(mode):
            url = get_resource_url(resource)
            result.append(render_resource(resource, url))
        return '\n'.join(result)

def apply_mode(resources, mode):
    result = []
    for resource in resources:
        result.append(resource.mode(mode))
    return result

def remove_duplicates(resources):
    """Given a set of resources, consolidate them so resource only occurs once.
    """
    seen = set()
    result = []
    for resource in resources:
        if resource.key() in seen:
            continue
        seen.add(resource.key())
        result.append(resource)
    return result

def consolidate(resources):
    # first map rollup -> list of resources that are in this rollup
    rollup_to_resources = {}   
    for resource in resources:
        for rollup in resource.part_of:
            rollup_to_resources.setdefault(rollup.key(), []).append(resource)

    # now replace resource with rollup consolidated biggest amount of
    # resources, or keep resource if no such rollup exists
    result = []
    for resource in resources:
        potential_rollups = []
        for rollup in resource.part_of:
            potential_rollups.append((len(rollup_to_resources[rollup.key()]),
                                      rollup))
        if not potential_rollups:
            # no rollups at all
            result.append(resource)
            continue
        sorted_rollups = sorted(potential_rollups)
        amount, rollup = sorted_rollups[-1]
        if amount > 1:
            result.append(rollup)
        else:
            result.append(resource)
    return result

def render_css(url):
    return ('<link rel="stylesheet" type="text/css" href="%s" />' %
            url)

def render_kss(url):
    raise NotImplementedError

def render_js(url):
    return ('<script type="text/javascript" src="%s"></script>' %
            url)

resource_renderers = {
    '.css': render_css,
    '.kss': render_kss,
    '.js': render_js,
    }

def render_resource(resource, url):
    renderer = resource_renderers.get(resource.ext(), None)
    if renderer is None:
        raise UnknownResourceExtension(
            "Unknown resource extension %s for resource: %s" %
            (resource.ext(), repr(resource)))
    return renderer(url)
