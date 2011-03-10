=============
megrok.nozodb
=============

The main purpose of this package is to provide support for 
enabling Grok applications to be run as aster served WSGI
applications without using the zodb.


Using megrok.nozodb
-------------------

To setup a grok environment which works without the zodb you 
have to replace the paster-application-factory which typically is
located in the debug.ini and in the deploy.ini: To be concrete
replace grokcore.startup#... with megrok.nozodb#nozodb

    [app:grok]
    use = egg:megrok.nozodb#nozodb


The next you have to do is setting up global utility which
acts as an ApplicationRoot which is a  starting point for your application. 
megrok.nozodb has an ungrokked default one.  You can subclass from it or 
provide your own stuff which acts as ApplicationRoot.

   >>> from megrok.nozodb import ApplicationRoot

   >>> class MyApplicationRoot(ApplicationRoot):
   ...     pass

   >>> myapp = MyApplicationRoot()

   >>> from grokcore.site.interfaces import IApplication
   >>> IApplication.providedBy(myapp)
   True

   >>> from zope.location import ILocation
   >>> ILocation.providedBy(myapp)
   True

   >>> from zope.interface.verify import verifyObject
   >>> from zope.component.interfaces import ISite
   >>> verifyObject(ISite, myapp)
   True


API Documentation
-----------------

We have to create a simple site definition file, which is also quite
plain::

   >>> import os, tempfile
   >>> temp_dir = tempfile.mkdtemp()

   >>> sitezcml = os.path.join(temp_dir, 'site.zcml')
   >>> open(sitezcml, 'w').write('<configure />')

   >>> zope_conf = os.path.join(temp_dir, 'zope.conf')
   >>> open(zope_conf, 'wb').write('''
   ... site-definition %s
   ...
   ... <zodb>
   ... </zodb>
   ...
   ... <eventlog>
   ...   <logfile>
   ...     path STDOUT
   ...   </logfile>
   ... </eventlog>
   ... ''' %sitezcml)


   >>> from megrok.nozodb import nozodb_factory
   >>> app_factory = nozodb_factory({'zope_conf': zope_conf})

  Clean up the temp_dir

    >>> import shutil
    >>> shutil.rmtree(temp_dir)

