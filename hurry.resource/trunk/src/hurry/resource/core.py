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
                  consolidated resource. This can be a path to the
                  larger resource in the same library, or a fully
                  specified ResourceSpec.
        key word arguments - different paths that represent the same
                  resource in different modes (debug, minified, etc),
                  or alternatively a fully specified ResourceSpec.
        """
        self.library = library
        self.relpath = relpath
        self.part_of = part_of
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

    def consolidated(self):
        """Get the resource spec in consolidated form.

        A resource can be part of a larger resource. Returns the
        resource spec of the consolidated resource, or None if no
        such larger resource exists.
        """
        if self.part_of is None:
            return None
        if isinstance(self.part_of, ResourceSpec):
            return self.part_of
        return ResourceSpec(self.library, self.part_of)
    
    def key(self):
        # XXX has to be a tuple right now as consolidation code depends
        # on this
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
    consolidated = {}
    processed = []
    for resource in resources:
        c = resource.consolidated()
        if c is None:
            processed.append(resource)
        else:
            processed.append(c.key())
            r = consolidated.setdefault(c.key(), [])
            r.append(resource)
    result = []
    for resource in processed:
        if type(resource) is TupleType:
            key = resource
            r = consolidated[key]
            if len(r) == 1:
                result.append(r[0])
            else:
                result.append(r[0].consolidated())
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
