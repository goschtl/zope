from zope.interface import Interface
from zope.configuration.xmlconfig import include, includeOverrides
from zope.configuration.fields import GlobalObject
from zope.dottedname.resolve import resolve
from zope.schema import TextLine

from z3c.autoinclude.dependency import DependencyFinder
from z3c.autoinclude.utils import debug_includes
from z3c.autoinclude.utils import distributionForPackage
from z3c.autoinclude.plugin import PluginFinder

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
    info = DependencyFinder(dist).includableInfo(['overrides.zcml'])
    includeZCMLGroup(_context, dist, info, 'overrides.zcml', override=True)

def autoIncludeDirective(_context, package):
    dist = distributionForPackage(package)
    info = DependencyFinder(dist).includableInfo(['configure.zcml', 'meta.zcml'])

    includeZCMLGroup(_context, dist, info, 'meta.zcml')
    includeZCMLGroup(_context, dist, info, 'configure.zcml')

class IIncludePluginsDirective(Interface):
    """Auto-include any ZCML in the dependencies of this package."""
    
    package = GlobalObject(
        title=u"Package to auto-include for",
        description=u"""
        Auto-include all dependencies of this package.
        """,
        required=True,
        )

    file = TextLine(
        title=u"ZCML filename to look for",
        description=u"Name of a ZCML file to look for; if omitted, autoinclude will scan for (meta, configure, overrides)",
        required=False,
        )

def includePluginsDirective(_context, package, file=None):
    dist = distributionForPackage(package)
    dotted_name = package.__name__
    if file is None:
        zcml_candidates = ['meta.zcml', 'configure.zcml', 'overrides.zcml']
    else:
        zcml_candidates = [file]
    info = PluginFinder(dotted_name).includableInfo(zcml_candidates)

    for file in zcml_candidates:
        override = False
        if file == 'overrides.zcml':
            # XXX this is really a hack
            # parallel to <includeOverrides> this should be a separate directive <includePluginsOverrides>
            override = True
        includeZCMLGroup(_context, dist, info, file, override=override)

import warnings
def deprecatedAutoIncludeDirective(_context, package):
    warnings.warn("The <autoinclude> directive is deprecated and will be removed in z3c.autoinclude 0.3. Please use <includeDependencies> instead.", DeprecationWarning, stacklevel=2)
    autoIncludeDirective(_context, package)

def deprecatedAutoIncludeOverridesDirective(_context, package):
    warnings.warn("The <autoincludeOverrides> directive is deprecated and will be removed in z3c.autoinclude 0.3. Please use <includeDependenciesOverrides> instead.", DeprecationWarning, stacklevel=2)
    autoIncludeOverridesDirective(_context, package)

