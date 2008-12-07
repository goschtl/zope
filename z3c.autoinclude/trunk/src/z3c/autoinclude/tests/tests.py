import doctest
import unittest

import os
from zc.buildout import testing
from pprint import pprint
projects_dir = os.path.dirname(__file__)
from pkg_resources import working_set


# this is the list of test packages that we'll temporarily install
# for the duration of the tests; you MUST add your test package name
# to this list if you want it to be available for import in doctests!
test_packages = ['APackage', 'BCPackage', 'XYZPackage',
                 'SiblingPackage', 'BasePackage', 'FooPackage',
                 'base2', 'base2_plug', 'TestDirective']


def install_projects(projects, target_dir):
    from zc.buildout.easy_install import install

    links = []
    for project in projects:
        project_dir = os.path.join(projects_dir, project)
        dist_dir = os.path.join(project_dir, 'dist')
        if os.path.isdir(dist_dir):
            testing.rmdir(dist_dir)
        dummy = testing.system("%s setup %s bdist_egg" % (
                os.path.join('bin', 'buildout'), project_dir))
        links.append(dist_dir)

    return install(projects, target_dir, links=links,
                   working_set=working_set)


def testSetUp(test):

    testing.buildoutSetUp(test)
        
    import tempfile
    target_dir = tempfile.mkdtemp('.z3c.autoinclude.test-installs')
    
    ws = install_projects(test_packages, target_dir)

    # we must perform a magical incantation on each distribution
    for dist in ws:
        dist.activate()
        
        if dist.project_name == 'APackage':
            test.globs['a_dist'] = dist
        elif dist.project_name == 'XYZPackage':
            test.globs['xyz_dist'] = dist
        elif dist.project_name == 'SiblingPackage':
            test.globs['sibling_dist'] = dist
        elif dist.project_name == 'FooPackage':
            test.globs['foo_dist'] = dist
        elif dist.project_name == 'BasePackage':
            test.globs['base_dist'] = dist


def test_suite():
    suite = doctest.DocFileSuite('../utils.txt', '../dependency.txt', '../plugin.txt',
                                 setUp=testSetUp,
                                 tearDown=testing.buildoutTearDown,
                                 globs={'pprint':pprint},
                                 optionflags=doctest.ELLIPSIS)

    return unittest.TestSuite((suite,
                               ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
