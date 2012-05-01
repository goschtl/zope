import zope.interface
import zope.interface.declarations
import martian
import fanstatic.core
import grokcore.resource.interfaces

def validateInclusion(directive, *resources):
    for resource in resources:
        if not isinstance(resource, fanstatic.core.Dependable):
            raise ValueError(
                'You can only include fanstatic Dependable '
                '(Resource or Group) components.')

class include(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE
    validate = validateInclusion

    def factory(self, *resources):
        zope.interface.declarations.addClassAdvisor(
            _resources_advice, depth=3)
        return resources

def _resources_advice(cls):
    if include.bind().get(cls):
        if not grokcore.resource.interfaces.IResourcesIncluder.implementedBy(
                cls):
            zope.interface.classImplements(
                cls,
                grokcore.resource.interfaces.IResourcesIncluder)
    return cls
