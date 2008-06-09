========================
lovely.zetup with paste
========================

This example shows how to configure lovely.zetup as a wsgi
application with the whole zope functionality but without the
need of a ZODB storage and without zconfig.

All config files reside in the testing subdirectory.

    >>> import lovely.zetup, os
    >>> testDir = os.path.join(os.path.dirname(lovely.zetup.__file__),
    ...                        'testing')

Let ust first have a look at the paste config file. Via the use option
we tell paste to use the lovely.zetup appfactory. The cfg options
describes the relative path from this config file to the application
specific config file which will be shown further down.

    >>> print file(os.path.join(testDir, 'paste.ini')).read()
    [app:main]
    use = egg:lovely.zetup
    cfg = testing.py
    logging = off

Note: The logging off switch means we don't enable logging
configuration at all. We need this in testing because the zope
testrunner somehow adds a NullHandler to the logger which then cannot
be removed anymore.

Application Configuration File
==============================

All configuration files are written in python. Below we see the
contents of the application configuraton for this example.

    >>> cfgFile = os.path.join(testDir, 'testing.py')
    >>> cfg = {}
    >>> execfile(cfgFile, {}, cfg)

The config file has to define local variables - 'app' and an optional
'sites' dictionary.

    >>> from pprint import pprint

The app dictionary
------------------

    >>> pprint(sorted(cfg['app'].items()))
    [('features', ['devmode']),
     ('logging', 'logging.cfg'),
     ('zcml', 'ftesting.zcml')]

The logging key defines which config file should be used to
configure logging. This is actually a standard logging config file as
described in
http://docs.python.org/lib/logging-config-fileformat.html.

The zcml key defines the path to the site's zcml file. And the
'features' key is a list of named features to be enabled.


The sites dictionary
--------------------

The sites dictionary is optional and defines the objects to be created
upon startup along with config. The created objects do not
necessarily need to be sites, but it is a common use-case to have
sites below root - each with its own configuration.

Each key in this dict is a site name.

    >>> sites = cfg['sites']
    >>> sites.keys()
    [u'testsite', u'secondsite']


There is one required key, which defines the IFactory utility to use
as factory for the instantiation of the site object. In some cases
this might be a custom site implementation, but for this test we just
use the normal zope folder factory.

    >>> sites['testsite']['factory']
    'zope.app.content.Folder'

The settings key is just a custom example entry. Any item
defined is available via the site object at runtime. So arbitrary
configuration can be applied for special cases.

    >>> sites['testsite']['settings']
    {'testing.option1': 1}

Each key defined in the ``configurator`` item defines which
configurator with the given name should be run on the created
object. For further information on configurators see the documentation
of z3c.configurator.

We have 2 configurators configured.

    >>> pprint(sites['testsite']['configurators'])
    {'testconfigurator.one': {'alist': ['server1:11211', 'server2:11211'],
                              'someunicode': u'noreply@example.com'},
     'testconfigurator.two': {'afloat': 1.0, 'astring': 'Value of Name'}}

The running Application
=======================

Let us now start our example application. We do this with the paste
test fixture. 

    >>> from paste.fixture import TestApp
    >>> app = TestApp('config:paste.ini',
    ...               relative_to=testDir)
    called: 'ConfTwo', on u'testsite' with data:
    {'afloat': 1.0, 'astring': 'Value of Name'}
    called: 'ConfOne', on u'testsite' with data:
    {'someunicode': u'noreply@example.com',
     'alist': ['server1:11211', 'server2:11211']}
    called: 'ConfTwo', on u'secondsite' with data:
    {'afloat': 1.0, 'astring': 'Value of Name'}
    called: 'ConfOne', on u'secondsite' with data:
    {'someunicode': u'noreply@example.com', 'alist':
    ['server1:11211', 'server2:11211']}

The example configurators we configured above are for testing and just
print out some information when called. So therefore the printouts
above. You see that each configurator is called twice because
we defined two sites in our ``testing.cfg`` with the same config file.

Now we should have a root object that can be traversed.

    >>> app.get('/@@absolute_url').body
    'http://localhost'

And the two site objects.

    >>> app.get('/testsite/@@absolute_url').body
    'http://localhost/testsite'
    >>> app.get('/secondsite/@@absolute_url').body
    'http://localhost/secondsite'

The default contents view of the Rotterdam skin needs principal annotations.
This package overwrites the content views for IFolder.

    >>> from base64 import b64encode
    >>> mgrHeaders = {'Authorization':'Basic %s' % b64encode('mgr:pw')}
    >>> app.get('/@@contents.html', headers=mgrHeaders)
    <Response 200 Ok '<!DOCTYPE html PUBLI'>

The contents view for the site manager still has this problem.

    >>> app.get('/++etc++site/@@contents.html', headers=mgrHeaders)
    Traceback (most recent call last):
    ...
    AppError: Bad response: 500 Internal Server Error (not 200 OK or 3xx redirect for /++etc++site/@@contents.html)
    <html><title>System Error</title>
    <body>
      A system error occurred.
    </body>
    </html>

We can disable the error handling by the server by setting a wsgi
environment variable. So we can investigate the error.

    >>> env = {'wsgi.handleErrors': False}
    >>> app.get('/++etc++site/@@contents.html', headers=mgrHeaders,
    ...         extra_environ=env)
    Traceback (most recent call last):
    ...
    TypeError: ('Could not adapt',
    <zope.app.security.principalregistry.Principal object at ...>,
    <InterfaceClass zope.annotation.interfaces.IAnnotations>)

We can do the same the way zope's testbrowser is doing it.

    >>> env = {'HTTP_X_ZOPE_HANDLE_ERRORS': 'False'}
    >>> app.get('/++etc++site/@@contents.html', headers=mgrHeaders,
    ...         extra_environ=env)
    Traceback (most recent call last):
    ...
    TypeError: ('Could not adapt',
    <zope.app.security.principalregistry.Principal object at ...>,
    <InterfaceClass zope.annotation.interfaces.IAnnotations>)

So the reason is that we have no principal annotation which is used to
hold copy/paste info in the skin. So far this should not be a problem,
because the only thing we need in zmi so far is the error report view
and this works ;-)

    >>> app.get('/++etc++site/errors/@@index.html', headers=mgrHeaders)
    <Response 200 Ok '<!DOCTYPE html PUBLI'>

Not all views of ++etc++process are available but runtime information
can be viewed.

    >>> app.get('/++etc++process/index.html', headers=mgrHeaders)
    <Response 200 Ok '<!DOCTYPE html PUBLI'>

XMLRPC Calls
============

XML-RPC requests are hanlded with the xmlrpc request factory. Actually
this is a fault because we have not body.

    >>> body = """<?xml version='1.0'?>
    ... <methodCall>
    ... <methodName>contents</methodName>
    ... <params>
    ... </params>
    ... </methodCall>
    ... """

We get a folder listing here

    >>> res = app.post('/', params=body, headers={'Content-Type':'text/xml'})
    >>> print res.body
    <?xml version='1.0'?>
    <methodResponse>
    <params>
    <param>
    <value><array><data>
    <value><string>testsite</string></value>
    <value><string>secondsite</string></value>
    </data></array></value>
    </param>
    </params>
    </methodResponse>
    <BLANKLINE>
