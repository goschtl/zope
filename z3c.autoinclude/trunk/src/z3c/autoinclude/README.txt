============================
Auto inclusion of zcml files
============================

This package provides a facility to automatically load zcml files
such as configure.zcml and meta.zcml for a project's dependencies
and extension packages.

Autoinclusion is signalled by custom zcml directives defined in
z3c.autoinclude's meta.zcml file.

To trigger autoinclusion of a package's dependencies, include the
following directive::

  <includeDependencies package='.' />

To trigger autoinclusion of a package's extensions, include the
following directive::

  <includePlugins package='.' />

And to signal a package as an extension to a base package, use
the following entry point (in your project's setup.py)::

  [z3c.autoinclude.plugin]
  target = basepackage.dotted.modulename


Automatic inclusion of package dependencies
===========================================

The z3c.autoinclude.dependency module uses an egg's install_requires
information (in the project's setup.py) to find and implicitly load
zcml from all dependencies of a project.

We have created a test environment to simulate setuptools
dependencies.

``APackage`` depends on ``BCPackage``
``BCPackage`` depends on ``SiblingPackage``

First, we need to have some infrastructure to install projects::

    >>> from zc.buildout.easy_install import install
    >>> from pkg_resources import working_set
    >>> import os
    >>> def install_projects(projects, target_dir):
    ...  links = []
    ...  for project in projects:
    ...    project_dir = join(projects_dir, project)
    ...    dist_dir = join(project_dir, 'dist')
    ...    if os.path.isdir(dist_dir):
    ...      rmdir(dist_dir)
    ...    dummy = system(join('bin', 'buildout') + ' setup ' + \
    ...              project_dir + ' bdist_egg')
    ...    links.append(dist_dir)
    ...
    ...  return install(projects, target_dir, links=links,
    ...                 working_set=working_set)

We ensure the projects are installed into a temporary directory so
that we can use them in our tests::

    >>> target_dir = tmpdir('target_dir')
    >>> ws = install_projects(['APackage', 'BCPackage', 'XYZPackage',
    ...                        'SiblingPackage', 'TestDirective'],
    ...                       target_dir)
    >>> for dist in ws:
    ...   dist.activate()
    ...   if dist.project_name == 'APackage':
    ...     a_dist = dist
    ...   if dist.project_name == 'XYZPackage':
    ...     xyz_dist = dist
    ...   if dist.project_name == 'SiblingPackage':
    ...	    sibling_dist = dist

Given the distribution for the project named ``APackage``, we can ask
for the requirements of that distribution::

    >>> reqs = a_dist.requires()
    >>> pprint(sorted(reqs, key=lambda r:r.project_name))
    [Requirement.parse('BCPackage'),
     Requirement.parse('TestDirective'),
     Requirement.parse('z3c.autoinclude')]

We can turn this requirement into a distribution::

    >>> from pkg_resources import get_provider
    >>> b_dist = get_provider(reqs[0])

We can adapt a distribution to a DependencyFinder::

    >>> from z3c.autoinclude.dependency import DependencyFinder
    >>> a_include_finder = DependencyFinder(a_dist)
    >>> b_include_finder = DependencyFinder(b_dist)
    >>> xyz_include_finder = DependencyFinder(xyz_dist)
    >>> sibling_include_finder = DependencyFinder(sibling_dist)

The include finder provides functionality to determine what namespace
packages exist in the distribution. In the case of ``APackage``, there
are no namespace packages::

    >>> a_include_finder.namespaceDottedNames()
    []

``BPackage`` does have a namespace package, ``b``::

    >>> b_include_finder.namespaceDottedNames()
    ['b']

``XYZPackage`` has a namespace package too, ``x.y`` (``x`` is also
a namespace package)::

    >>> xyz_include_finder.namespaceDottedNames()
    ['x', 'x.y']

We can also get the dotted names of the actual packages that we want
to inspect in a distribution. For a project without namespace packages,
this will be the packages directly in the packages::

    >>> a_include_finder.dottedNames()
    ['a']

For a project with namespace packages, it will be the packages that
are in the namespace packages::

    >>> b_include_finder.dottedNames()
    ['b.c']

For a nested namespace package, it should still be the innermost package::

    >>> xyz_include_finder.dottedNames()
    ['x.y.z']

What we need to know in the end is which packages in the requirements
of a distribution have files we want to include (``configure.zcml``,
``meta.zcml``). So, given a distribution, let's retrieve all packages
that it depends on that have ``configure.zcml`` or ``meta.zcml``.
Note that the individual lists within ``includableInfo`` preserve the
package order defined in ``setup.py``::

    >>> a_include_finder.includableInfo(['configure.zcml', 'meta.zcml'])
    {'configure.zcml': ['b.c'], 'meta.zcml': ['z3c.autoinclude', 'testdirective']}

For a nested namespace package with two siblings ``SiblingPackage``,
we should get the same expected results. The sibling package
``SiblingPackage`` does have a namespace package::

    >>> sibling_include_finder.namespaceDottedNames()
    ['F']

For a namespace package with 2 sibling namespaces, we get both sibling
packages::

    >>> sibling_include_finder.dottedNames()
    ['F.G', 'F.H']

And we should be able to pick up the files we need to include from
both dotted names::

    >>> pprint(b_include_finder.includableInfo(['configure.zcml',
    ...                                         'meta.zcml']))
    {'configure.zcml': ['F.H'], 'meta.zcml': ['testdirective', 'F.G', 'F.H']}

``APackage`` depends on ``BCPackage``, which depends on
``SiblingPackage``. ``APackage`` and ``BCPackage`` both contain the
autoinclude directive, which will automatically include any meta.zcml
and configure.zcml files (in that order) that their dependencies
contain. These dependencies' zcml actually contain a test directive
that will append a logging message to a global variable in
testdirective.zcml. So let's trigger the loading of the configure.zcml
in ``APackage`` and see whether its ``BCPackage`` dependency, and
``BCPackage``'s dependencies, were indeed loaded and in the correct
order::

    >>> from pkg_resources import resource_filename
    >>> from zope.configuration import xmlconfig
    >>> import a
    >>> dummy = xmlconfig.file(resource_filename('a', 'configure.zcml'),
    ...                        package=a)
    >>> from testdirective.zcml import test_log
    >>> pprint(test_log)
    [u'f.g meta has been loaded',
     u'f.h has been loaded',
     u'BCPackage has been loaded']

There is also a directive for including overrides, which calls
``autoIncludeOverridesDirective``; however, I have no idea how to test
this.

Finally, there is a convenience API for finding the files we need to
include from the requirements of a given package::

    >>> from z3c.autoinclude import package_includes
    >>> pprint(package_includes('BCPackage'))
    {'configure.zcml': ['F.H'], 'meta.zcml': ['testdirective', 'F.G', 'F.H']}

As with ``includableInfo``, we can also supply a list of ZCML filenames to search for::

    >>> pprint(package_includes('BCPackage', ['configure.zcml', 'silly.zcml']))
    {'configure.zcml': ['F.H']}
    
Note that it will not catch DistributionNotFound errors::

     >>> package_includes('NonexistentPackage')
     Traceback (most recent call last):
     ...
     DistributionNotFound: NonexistentPackage

Now let's just clean up our test log in preparation for the next test::

    >>> from testdirective.zcml import clear_test_log
    >>> clear_test_log()
    >>> pprint(test_log)
    []


=========================================
Automatic inclusion of extension packages
=========================================

There is additional functionality for registering and autoincluding
extension packages for a particular platform.

In this test environment, ``BasePackage`` provides the ``basepackage``
module which we will treat as our platform.  ``FooPackage`` wants to
broadcast itself as a plugin for ``basepackage`` and thereby register
its ZCML as a candidate for automatic inclusion. ``TestDirective``
also broadcasts itself as a plugin for ``basepackage``.

So, once again, we must first set up our testing infrastructure::

    >>> ws = install_projects(['BasePackage', 'FooPackage', 'TestDirective',
    ...                        'base2', 'base2_plug'],
    ...                       target_dir)
    >>> for dist in ws:
    ...   dist.activate()
    ...   if dist.project_name == 'FooPackage':
    ...     foo_dist = dist
    ...   elif dist.project_name == 'BasePackage':
    ...     base_dist = dist

Given a module name, we can ask for distributions which have been broadcast
themselves as plugging into that module via entry points::

    >>> from z3c.autoinclude.plugin import find_plugins
    >>> sorted(find_plugins('basepackage'))
    [FooPackage 0.0 (...), TestDirective 0.0 (...)]

Armed with a valid module name we can find the ZCML files within it
which must be loaded::

    >>> from z3c.autoinclude.plugin import zcml_to_include
    >>> zcml_to_include('foo')
    ['configure.zcml']

By default the function looks for the standard ZCML files ``meta.zcml``,
``configure.zcml``, and ``overrides.zcml`` but this behavior can be
overridden::

    >>> zcml_to_include('foo', ['meta.zcml'])
    []

Finally, we know how to get a list of all module dottednames within
a distribution, through the DistributionManager adapter::

    >>> from z3c.autoinclude.utils import DistributionManager
    >>> DistributionManager(foo_dist).dottedNames()
    ['foo']

So between these functions we can now get a dictionary of all
extension modules which must be loaded for each ZCML group given
a base platform.

For consistency, we use the same API as with dependency autoinclusion.
This time we adapt a base platform (represented by a string referring
to an importable dotted module name) to a PluginFinder and call its
`includableInfo` method::

    >>> from z3c.autoinclude.plugin import PluginFinder
    >>> pprint(PluginFinder('basepackage').includableInfo(['configure.zcml',
    ...                                                    'meta.zcml']))
    {'configure.zcml': ['foo'], 'meta.zcml': ['testdirective']}

``FooPackage`` has a test-logging directive in its configure.zcml
which is defined in meta.zcml in ``TestDirective``.  ``FooPackage``
does not know anything about ``TestDirective`` and does not explicitly
include its ZCML; so for the test-logging directive to succeed when
the ZCML of ``FooPackage`` is loaded, the meta.zcml from ``TestDirective``
must be loaded first.  Since ``TestDirective`` offers itself as a
plugin for ``BasePackage`` and zcmlgroups are loaded in the
conventional order with all meta.zcml first, none of this should
explode when we load the ZCML from ``BasePackage`` and the test log
should accurately reflect that the ``FooPackage`` ZCML has been loaded::

    >>> import basepackage
    >>> dummy = xmlconfig.file(resource_filename('basepackage', 'configure.zcml'),
    ...                        package=basepackage)
    >>> pprint(test_log)
    [u'foo has been loaded']

``base2`` is a namespace package. ``base2.plug`` is a package that
defines a plugin for base2; it extends ``base2``s namespace.

    >>> clear_test_log()
    >>> import base2
    >>> from pkg_resources import Requirement, resource_filename
    >>> req = Requirement.parse('base2')
    >>> import os
    >>> filename = resource_filename(req, os.path.join('base2', 'configure.zcml'))
    >>> dummy = xmlconfig.file(filename, package=base2)
    >>> pprint(test_log)
    [u'base2.plug has been loaded']


=================
Utility functions
=================

Though this isn't the best place for these tests, I don't want to
extract out the testing infrastructure right now; so let's just
test the z3c.autoinclude.utils module right here.

distributionForPackage is a function that takes a module object
and returns the setuptools distribution object that contains
the module.

It should find the correct distribution for a package whose namespace
is extended by other packages in the environment::

    >>> from z3c.autoinclude.utils import distributionForPackage
    >>> distributionForPackage(base2)
    base2 0.0 (...base2-0.0...egg)

It should also find the correct distribution for namespace packages,
even if the namespace being extended is a module defined in another
package in the environment::

    >>> import base2.plug
    >>> distributionForPackage(base2.plug)
    base2-plug 0.0 (...base2_plug-0.0...egg)

While we're at it, it should also find the correct distribution for
packages whose distribution name has no bearing on the name of the
package contained within it::

    >>> import basepackage
    >>> distributionForPackage(basepackage)
    BasePackage 0.0 (...BasePackage-0.0...egg)

    >>> import foo
    >>> distributionForPackage(foo)
    FooPackage 0.0 (...FooPackage-0.0...egg)
