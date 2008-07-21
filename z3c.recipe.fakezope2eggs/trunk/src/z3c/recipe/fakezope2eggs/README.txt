Here is the most basic example::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts =
    ...     zope2
    ...     fakezope2eggs
    ...
    ... find-links =
    ...     http://dist.plone.org/
    ...
    ... [zope2]
    ... recipe = plone.recipe.zope2install
    ... url = http://www.zope.org/Products/Zope/2.9.7/Zope-2.9.7-final.tgz
    ...
    ... [fakezope2eggs]
    ... recipe = z3c.recipe.fakezope2eggs
    ... """)

Now if we run the buildout::

    >>> print system(buildout)
    Installing zope2.
    running build_ext
    creating zope.proxy
    copying zope/proxy/proxy.h -> zope.proxy
    building 'AccessControl.cAccessControl' extension
    creating build
    creating build/temp.linux-i686-2.4
    creating build/temp.linux-i686-2.4/AccessControl
    ...

Now if we list all the developped egg we have:

    >>> ls(sample_buildout, 'develop-eggs')
    -  plone.recipe.zope2install.egg-link
    -  z3c.recipe.fakezope2eggs.egg-link
    -  zope.app.adapter.egg-info
    -  zope.app.annotation.egg-info
    -  zope.app.apidoc.egg-info
    -  zope.app.applicationcontrol.egg-info
    -  zope.app.appsetup.egg-info
    -  zope.app.authentication.egg-info
    -  zope.app.basicskin.egg-info
    -  zope.app.broken.egg-info
    -  zope.app.cache.egg-info
    ...

Let's have a look at the content of one of them::

    >>> cat(sample_buildout, 'develop-eggs', 'zope.app.adapter.egg-info')
    Metadata-Version: 1.0
    Name: zope.app.adapter
    Version: 0.0

You might also want to add other fake eggs to your buildout, to do so use the
additional-fake-eggs option, for example::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts =
    ...     zope2
    ...     fakezope2eggs
    ...
    ... find-links =
    ...     http://dist.plone.org/
    ...
    ... [zope2]
    ... recipe = plone.recipe.zope2install
    ... url = http://www.zope.org/Products/Zope/2.9.7/Zope-2.9.7-final.tgz
    ...
    ... [fakezope2eggs]
    ... recipe = z3c.recipe.fakezope2eggs
    ... additional-fake-eggs = ZODB3
    ... """)

    >>> print system(buildout)
    Uninstalling fakezope2eggs.
    Updating zope2.
    Installing fakezope2eggs.
    <BLANKLINE>

Let's check if the additionnal fake egg exists:

    >>> cat(sample_buildout, 'develop-eggs', 'ZODB3.egg-info')
    Metadata-Version: 1.0
    Name: ZODB3
    Version: 0.0

