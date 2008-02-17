import sys

from pkg_resources import find_distributions
from zope.interface import Interface
from zope.configuration.xmlconfig import include, includeOverrides
from zope.configuration.fields import GlobalObject
from zope.dottedname.resolve import resolve

from z3c.autoinclude.include import IncludeFinder
from z3c.autoinclude.include import debug_includes

class IAutoIncludeDirective(Interface):
    """Auto-include any ZCML in the dependencies of this package."""
    
    package = GlobalObject(
        title=u"Package to auto-include for",
        description=u"""
        Auto-include all dependencies of this package.
        """,
        required=True,
        )

def autoIncludeOverridesDirective(_context, package):
    dist = distributionForPackage(package)
    info = IncludeFinder(dist).includableInfo(['overrides.zcml'])

    overrides_zcml = list(info.get('overrides.zcml', []))
    debug_includes(dist, 'overrides.zcml', overrides_zcml)
    for dotted_name in overrides_zcml:
        dependency_package = resolve(dotted_name)
        includeOverrides(_context, 'overrides.zcml', dependency_package)

def autoIncludeDirective(_context, package):
    dist = distributionForPackage(package)
    info = IncludeFinder(dist).includableInfo(['configure.zcml', 'meta.zcml'])

    meta_zcml = list(info.get('meta.zcml', []))
    debug_includes(dist, 'meta.zcml', meta_zcml)
    for dotted_name in meta_zcml:
        dependency_package = resolve(dotted_name)
        include(_context, 'meta.zcml', dependency_package)

    configure_zcml = list(info.get('configure.zcml', []))
    debug_includes(dist, 'configure.zcml', configure_zcml)
    for dotted_name in configure_zcml:
        dependency_package = resolve(dotted_name)
        include(_context, 'configure.zcml', dependency_package)
    
def distributionForPackage(package):
    package_filename = package.__file__
    for path in sys.path:
        if package_filename.startswith(path):
            break
    return list(find_distributions(path, True))[0]
