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

Finally, remember to register the new package at ``etc/site.zcml``::

    <configure xmlns="http://namespaces.zope.org/zope"
      ...
      <include package="ldappas" />
      ...
    </configure>

If there is any new directive required for this package, you need to
include the configuration file where the directive is registered.
Normally the ZCML directives will be registered in meta package.  You
can use the ``file`` option as given below::

    <configure xmlns="http://namespaces.zope.org/zope"
      ...
      <include package="some.package" file="meta.zcml" />
      <include package="ldappas" />
      ...
    </configure>

And restart application::

  $ ./bin/paster serve debug.ini

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
