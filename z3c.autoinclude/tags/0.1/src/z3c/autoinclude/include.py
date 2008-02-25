import os
from zope.dottedname.resolve import resolve
from pkg_resources import resource_exists
from pkg_resources import get_provider
from pkg_resources import get_distribution
import logging

log = logging.getLogger("z3c.autoinclude")

class IncludeFinder(object):
    def __init__(self, dist):
        self.context = dist

    def namespaceDottedNames(self):
        """Return dotted names of all namespace packages in distribution.
        """
        try:
            return list(self.context.get_metadata_lines('namespace_packages.txt'))
        except IOError:
            return []
        
    def dottedNames(self):
        """Return dotted names of all relevant packages in a distribution.

        Relevant packages are those packages that are directly under the
        namespace packages in the distribution, but not the namespace packages
        themselves. If no namespace packages exist, return those packages that
        are directly in the distribution.
        """
        dist_path = self.context.location
        ns_dottednames = self.namespaceDottedNames()
        if not ns_dottednames:
            return subpackageDottedNames(dist_path)
        result = []
        for ns_dottedname in ns_dottednames:
            path = os.path.join(dist_path, *ns_dottedname.split('.'))
            result.extend(subpackageDottedNames(path, ns_dottedname))
        return result

    def includableInfo(self, include_candidates):
        """Return the packages in the dependencies which are includable.

        include_candidates - a list of include files we are looking for

        Returns a dictionary with the include candidates as keys, and lists
        of dotted names of packages that contain the include candidates as
        values.
        """
        result = {}
        for req in self.context.requires():
            include_finder = IncludeFinder(get_provider(req))
            for dotted_name in include_finder.dottedNames():
                module = resolve(dotted_name)
                for candidate in include_candidates:
                    candidate_path = os.path.join(
                        os.path.dirname(module.__file__), candidate)
                    if os.path.isfile(candidate_path):
                        result.setdefault(candidate, []).append(dotted_name)
        return result

    
def subpackageDottedNames(package_path, ns_dottedname=None):
    # we do not look for subpackages in zipped eggs
    if not os.path.isdir(package_path):
        return []

    result = []
    for subpackage_name in os.listdir(package_path):
        full_path = os.path.join(package_path, subpackage_name)
        if isPythonPackage(full_path):
            if ns_dottedname:
                result.append('%s.%s' % (ns_dottedname, subpackage_name))
            else:
                result.append(subpackage_name)
    return result

def isPythonPackage(path):
    if not os.path.isdir(path):
        return False
    for init_variant in ['__init__.py', '__init__.pyc', '__init__.pyo']:
        if os.path.isfile(os.path.join(path, init_variant)):
            return True
    return False

def package_includes(project_name, zcml_filenames=None):
    """
    Convenience function for finding zcml to load from requirements for
    a given project. Takes a project name. DistributionNotFound errors
    will be raised for uninstalled projects.
    """
    if zcml_filenames is None:
        zcml_filenames = ['meta.zcml', 'configure.zcml', 'overrides.zcml']
    dist = get_distribution(project_name)
    include_finder = IncludeFinder(dist)
    return include_finder.includableInfo(zcml_filenames)

def debug_includes(dist, include_type, dotted_names):
    if not dotted_names:
        return
    log.debug('%s - autoinclude %s: %r', dist.project_name,
              include_type, list(dotted_names))
