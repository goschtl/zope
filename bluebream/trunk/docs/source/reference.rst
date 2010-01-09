Reference
=========

zope.app.wsgi
-------------

- getWSGIApplication

::

  def getWSGIApplication(configfile, schemafile=None, features=(),
                         requestFactory=HTTPPublicationRequestFactory,
                         handle_errors=True):
      db = config(configfile, schemafile, features)
      application = WSGIPublisherApplication(db, requestFactory, handle_errors)

      # Create the application, notify subscribers.
      notify(interfaces.WSGIPublisherApplicationCreated(application))

      return application

The first argument "configfile" should an absolute path to
"zope.conf" file.  All other arguments are optional.  The
"schemafile" argument value will be the ZConfig schema (XXX: what is
ZConfig) file.  By default the value for "schemafile" will be
"schema/schema.xml" defined inside "zope.app.appsetup".

..
   It looks like the number of databases mentioned in "zope.conf" is
   not considered, Zope will use only one::

     # Connect to and open the database, notify subscribers.
     db = appsetup.multi_database(options.databases)[0][0]

   Is there any use case for opening multiple database configuration
   ?  May be for mounting ?

zope.annotation
---------------

zope.app.applicationcontrol
---------------------------

zope.app.appsetup
-----------------

zope.app.authentication
-----------------------

zope.app.basicskin
------------------

zope.app.broken
---------------

zope.app.component
------------------

zope.app.container
------------------

zope.app.content
----------------

zope.app.debug
--------------

zope.app.dependable
-------------------

zope.app.error
--------------

zope.app.folder
---------------

zope.app.form
-------------

zope.app.generations
--------------------

zope.app.i18n
-------------

zope.app.interface
------------------

zope.app.locales
----------------

zope.app.localpermission
------------------------

zope.app.pagetemplate
---------------------

zope.app.principalannotation
----------------------------

zope.app.publication
--------------------

zope.app.publisher
------------------

zope.app.renderer
-----------------

zope.app.rotterdam
------------------

zope.app.schema
---------------

zope.app.security
-----------------

zope.app.server
---------------

zope.app.testing
----------------

zope.app.twisted
----------------

zope.app.zopeappgenerations
---------------------------

zope.authentication
-------------------

zope.broken
-----------

zope.browser
------------

zope.browsermenu
----------------

zope.browserpage
----------------

zope.browserresource
--------------------

zope.cachedescriptors
---------------------

zope.component
--------------

zope.componentvocabulary
------------------------

zope.configuration
------------------

zope.container
--------------

zope.contenttype
----------------

zope.copy
---------

zope.copypastemove
------------------

zope.datetime
-------------

zope.deferredimport
-------------------

zope.deprecation
----------------

zope.dottedname
---------------

zope.dublincore
---------------

zope.error
----------

zope.event
----------

zope.exceptions
---------------

zope.filerepresentation
-----------------------

zope.formlib
------------

zope.hookable
-------------

zope.i18n
---------

zope.i18nmessageid
------------------

zope.interface
--------------

zope.lifecycleevent
-------------------

zope.location
-------------

zope.minmax
-----------

zope.pagetemplate
-----------------

zope.password
-------------

zope.principalannotation
------------------------

zope.principalregistry
----------------------

zope.processlifetime
--------------------

zope.proxy
----------

zope.ptresource
---------------

zope.publisher
--------------

zope.schema
-----------

zope.security
-------------

zope.securitypolicy
-------------------

zope.server
-----------

zope.session
------------

zope.site
---------

zope.size
---------

zope.structuredtext
-------------------

zope.tal
--------

zope.tales
----------

zope.testbrowser
----------------

zope.testing
------------

zope.traversing
---------------

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
