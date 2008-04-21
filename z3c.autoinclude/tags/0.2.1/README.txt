This package adds two new ZCML directives: "includeDependencies"
and "includePlugins".

The "includeDependencies" directive searches through the dependencies
in your setup.py file (install_requires), and includes the meta.zcml
and configure.zcml files in those packages that it finds. Inclusion
order matches the order in the setup.py file. You can pass a path for
the package you want to include dependencies for, but typically you
pass in the current package, as follows::

  <includeDependencies package="." />

The motivation behind this is to prevent having to repeat yourself in
two places when you want to depend on a Zope 3 or Grok-based
dependency: in the ``setup.py`` (in ``install_requires``) to make the
dependency known, and again in ``configure.zcml`` with an ``include``
statement to make sure the dependency's ZCML file are
included. Because you have to repeat yourself, you can easily make an
error where you add a new dependency in ``setup.py``, but forget to
include the ZCML as well. If your package uses the ``autoinclude``
directive, adding the includes for the ZCML configuration of
individual dependencies is no longer necessary.

The next versions of Grok_ and grokproject_ will use this functionality
out of the box. The grokproject command will automatically add the
``includeDependencies`` directive in the ZCML of the project it generates.
You can then stop worrying about manual ZCML inclusion in the vast
majority of cases.

The "includePlugins" directive uses entry points to find installed
packages that broadcast themselves as plugins to a particular base
package. You can pass a path for the package you want to include
plugins for, but typically you pass in the current package, as
follows::

  <includePlugins package="." />

To broadcast a package as a plugin to a base package called "my_base",
add the following lines to the plugin package's ``setup.py``::

  entry_points="""
  [z3c.autoinclude.plugin]
  target = my_base
  """

The z3c.autoinclude directives automatically include
``configure.zcml`` and ``meta.zcml`` files that live in the main
package directories. In some cases, a package may use unusual names or
locations for its ZCML files. In that case you will need to modify
your package's ``configure.zcml`` and ``meta.zcml`` yourself to
include the ZCML using the manual ``include`` directive.

To make the z3c.autoinclude directives available for use in your
application or framework, you need to include it (in your
``meta.zcml`` for instance), like this::

  <include package="z3c.autoinclude" file="meta.zcml" />

Grok already does this for you automatically.

.. _Grok: http://grok.zope.org

.. _grokproject: http://pypi.python.org/pypi/grokproject
