import os
from zope.dottedname.resolve import resolve
from pkg_resources import resource_exists
from pkg_resources import get_provider
from pkg_resources import get_distribution
from z3c.autoinclude.utils import DistributionManager

class DependencyFinder(DistributionManager):
    def includableInfo(self, include_candidates):
        """Return the packages in the dependencies which are includable.

        include_candidates - a list of include files we are looking for

        Returns a dictionary with the include candidates as keys, and lists
        of dotted names of packages that contain the include candidates as
        values.
        """
        result = {}
        for req in self.context.requires():
            dist_manager = DistributionManager(get_provider(req))
            for dotted_name in dist_manager.dottedNames():
                module = resolve(dotted_name)
                for candidate in include_candidates:
                    candidate_path = os.path.join(
                        os.path.dirname(module.__file__), candidate)
                    if os.path.isfile(candidate_path):
                        result.setdefault(candidate, []).append(dotted_name)
        return result

def package_includes(project_name, zcml_filenames=None):
    """
    Convenience function for finding zcml to load from requirements for
    a given project. Takes a project name. DistributionNotFound errors
    will be raised for uninstalled projects.
    """
    if zcml_filenames is None:
        zcml_filenames = ['meta.zcml', 'configure.zcml', 'overrides.zcml']
    dist = get_distribution(project_name)
    include_finder = DependencyFinder(dist)
    return include_finder.includableInfo(zcml_filenames)
