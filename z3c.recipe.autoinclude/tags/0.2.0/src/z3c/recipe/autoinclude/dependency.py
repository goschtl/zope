import os, sys, pkg_resources


class DependencyFinder(object):

    def __init__(self, dist, ws):
        self.context = dist
        self.ws = ws

    def paths(self):
        dist_path = self.context.location

        ns_paths = []
        for name in namespaceDottedNames(self.context):
            ns_paths.append(os.path.join(*name.split('.')))

        if not ns_paths:
            return subpackageDottedNames(dist_path)

        result = []
        for ns_path in ns_paths:
            path = os.path.join(dist_path, ns_path)
            subpackages = subpackageDottedNames(path, ns_path)
            for subpackage in subpackages:
                if subpackage not in ns_paths:
                    result.append(subpackage)
        return result

    def includableInfo(self, zcml_to_look_for, seen=None):
        result = dict([(key, []) for key in zcml_to_look_for])
        
        if seen is None:
            seen = set()

        seen.add(self.context.project_name)

        # process package requirenments
        for req in self.context.requires():
            pkg = req.project_name

            if pkg in seen or pkg == 'setuptools':
                continue

            # get info from requirenments
            dist = self.ws.find(req)
            if dist is None:
                continue

            info = DependencyFinder(
                self.ws.find(req), self.ws).includableInfo(zcml_to_look_for, seen)

            for key, items in info.items():
                data = result[key]
                for item in items:
                    if item not in data:
                        data.append(item)

        # get info for self
        for path in self.paths():
            for candidate in zcml_to_look_for:
                candidate_path = os.path.join(
                    self.context.location, path, candidate)

                if os.path.isfile(candidate_path):
                    result[candidate].append(self.context.project_name)

        return result


def subpackageDottedNames(package_path, ns_path=None):
    # we do not look for subpackages in zipped eggs
    if not os.path.isdir(package_path):
        return []

    result = []
    for subpackage_name in os.listdir(package_path):
        full_path = os.path.join(package_path, subpackage_name)
        if isPythonPackage(full_path):
            if ns_path:
                result.append(os.path.join(ns_path, subpackage_name))
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


def namespaceDottedNames(dist):
    try:
        ns_dottednames = list(dist.get_metadata_lines('namespace_packages.txt'))
    except IOError:
        ns_dottednames = []
    except KeyError:
        ns_dottednames = []
    return ns_dottednames
