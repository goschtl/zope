Adding new package dependency
=============================

.. warning::

   This documentation is under construction.  See the `Documentation
   Status <http://wiki.zope.org/bluebream/DocumentationStatus>`_ page
   in wiki for the current status and timeline.

.. based on: http://wiki.zope.org/zope3/HowDoIAddAnEggDependency

You are working in your instance or developing your package and then
you discover that there is a package you may find useful, let's say
'ldappas'.  Edit ``setup.py`` and add in ``install_requires`` the
name of the package::

    setup(name='ticketcollector'
          ...
          install_requires = ['setuptools',
                              ...
                              'ldappas',
                             ],
          ...

Now it is time to rebuild your application::

    $ ./bin/buildout

Finally, remember to register the new package at ``site.zcml``::

    <configure xmlns="http://namespaces.zope.org/zope"
      ...
      <include package="ldappas" />
      ...
    </configure>

And restart application::

  $ ./bin/paster serve debug.ini
