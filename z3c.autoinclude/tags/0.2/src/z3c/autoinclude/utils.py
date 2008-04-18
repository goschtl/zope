import logging
import os
from pkg_resources import find_distributions
import sys
from zope.dottedname.resolve import resolve

log = logging.getLogger("z3c.autoinclude")

class DistributionManager(object):
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

def distributionForPackage(package):

    package_filename = package.__file__
    for path in sys.path:
        if package_filename.startswith(path):
            break
    dists = list(find_distributions(path, True))
    assert dists, "No distributions found for package %s/%s" % (path, package_filename)
    return dists[0]

def distributionForDottedName(dotted_name):
    return distributionForPackage(resolve(dotted_name))

def debug_includes(dist, include_type, dotted_names):
    if not dotted_names:
        return
    log.debug('%s - autoinclude %s: %r', dist.project_name,
              include_type, list(dotted_names))
