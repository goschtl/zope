grokcore.startup
****************

Single functions
================

application_factory(global_conf, **local_conf)
----------------------------------------------

`grokcore.startup` provides a function `application_factory` which
delivers a `WSGIPublisherApplication` instance when called with an
appropriate configuration.

A call to this function is normally required as entry point in
`setuptools`-driven paster environments.

We have to create our own site definition file -- which will simply be
empty -- to provide a minimal test::

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()
  >>> sitezcml = os.path.join(temp_dir, 'site.zcml')
  >>> open(sitezcml, 'w').write('<configure />')

Furthermore we create a Zope configuration file, which is also quite
plain::

  >>> zope_conf = os.path.join(temp_dir, 'zope.conf')
  >>> open(zope_conf, 'wb').write('''
  ... site-definition %s
  ...
  ... <zodb>
  ...   <mappingstorage />
  ... </zodb>
  ...
  ... <eventlog>
  ...   <logfile>
  ...     path STDOUT
  ...   </logfile>
  ... </eventlog>
  ... ''' %sitezcml)

Now we can call `application_factory` to get a WSGI application::

  >>> from grokcore.startup.startup import application_factory
  >>> app_factory = application_factory(dict(zope_conf = zope_conf))
  >>> app_factory
  <zope.app.wsgi.WSGIPublisherApplication object at 0x...>

Clean up::

  >>> import shutil
  >>> shutil.rmtree(temp_dir)
