import sys

from pkg_resources import find_distributions
from zope.interface import Interface
from zope.configuration.xmlconfig import include, includeOverrides
from zope.configuration.fields import GlobalObject
from zope.dottedname.resolve import resolve

from z3c.autoinclude.include import IncludeFinder
from z3c.autoinclude.include import debug_includes
from z3c.autoinclude.plugin import plugins_to_include

class IAutoIncludeDirective(Interface):
    """Auto-include any ZCML in the dependencies of this package."""
    
    package = GlobalObject(
        title=u"Package to auto-include for",
        description=u"""
        Auto-include all dependencies of this package.
        """,
        required=True,
        )

def includeZCMLGroup(_context, dist, info, zcmlgroup, override=False):
    includable_zcml = list(info.get(zcmlgroup, []))
    debug_includes(dist, zcmlgroup, includable_zcml)
    for dotted_name in includable_zcml:
        includable_package = resolve(dotted_name)
        if override:
            includeOverrides(_context, zcmlgroup, includable_package)
        else:
            include(_context, zcmlgroup, includable_package)

def autoIncludeOverridesDirective(_context, package):
    dist = distributionForPackage(package)
    info = IncludeFinder(dist).includableInfo(['overrides.zcml'])
    includeZCMLGroup(_context, dist, info, 'overrides.zcml', override=True)

def autoIncludeDirective(_context, package):
    dist = distributionForPackage(package)
    info = IncludeFinder(dist).includableInfo(['configure.zcml', 'meta.zcml'])

    includeZCMLGroup(_context, dist, info, 'meta.zcml')
    includeZCMLGroup(_context, dist, info, 'configure.zcml')
    
def distributionForPackage(package):
    package_filename = package.__file__
    for path in sys.path:
        if package_filename.startswith(path):
            break
    return list(find_distributions(path, True))[0]

class IIncludePluginsDirective(Interface):
    """Auto-include any ZCML in the dependencies of this package."""
    
    package = GlobalObject(
        title=u"Package to auto-include for",
        description=u"""
        Auto-include all dependencies of this package.
        """,
        required=True,
        )

def includePluginsDirective(_context, package):
    dist = distributionForPackage(package)
    dotted_name = package.__name__
    info = plugins_to_include(dotted_name)

    includeZCMLGroup(_context, dist, info, 'meta.zcml')
    includeZCMLGroup(_context, dist, info, 'configure.zcml')
    includeZCMLGroup(_context, dist, info, 'overrides.zcml', override=True)
