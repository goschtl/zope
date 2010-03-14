
:doctest:
:layer: grokui.zodbbrowser.tests.GrokZODBBrowserFunctionalLayer

We start a testbrowser to browse a local ZODB:

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.handleErrors = True

When browsing the root folder, we will be redirected to the ZODB
browser, which is part of the grok UI framework:

    >>> browser.open('http://localhost/')
    >>> browser.url
    'http://localhost/++grokui++/@@zodbbrowser'

There is a link available, that will always bring us back to the ZODB
browsers root:

    >>> browser.getLink('ZODB browser')
    <Link text='ZODB browser' url='http://localhost/++grokui++/zodbbrowser'>

Every object stored in a ZODB has a unique object ID. If we know that
OID, we can browse the object directly:

    >>> from ZODB.utils import u64
    >>> root = getRootFolder()

The ``_p_oid`` attribute of a ZODB-stored object contains the OID as
binary data (8 bytes) that we transform into an int using the ``u64``
helper function from ``ZODB.utils``.

    >>> root_oid = u64(root._p_oid)
    >>> browser.open(
    ...     'http://localhost/++grokui++/@@zodbbrowser/%s' % root_oid)

A root folder normally contains a local site manager names
``_sm``. A link to this site manager is available:

    >>> browser.getLink('_sm')
    <Link text='_sm' url='http://localhost/++grokui++/zodbbrowser/...>

By default you will only see a limited set of member for each browsed
object, these members, which are stored in ZODB separated from the
currently browsed object. Not displayed are other members, that are
'native' attributes or methods of a browsed object.

    >>> 'getSiteManager(self)' in browser.contents
    False

You can, however, enable displaying of those members by ticking `show
all members` box and clicking the `Update` button:

    >>> browser.getControl('show all members')
    <ItemControl name='show_all' type='checkbox' ... selected=False>
    >>> browser.getControl('show all members').selected = True
    >>> browser.getControl('Update').click()

Now the ``getSiteManager()`` method is displayed:

    >>> 'getSiteManager(self)' in browser.contents
    True

We can also enable or disable displaying of doc strings of
members (disabled by default). For example the docstring for a folders
``keys()`` method tells us:

    >>> browser.getControl('show docstrings').selected = True
    >>> browser.getControl('Update').click()
    >>> print browser.contents
    <html xmlns="http://www.w3.org/1999/xhtml">
    ...
    ...<pre>Return a sequence-like object containing the names
    associated with the objects that appear in the folder</pre>
    ...

We disable both, displaying of docstrings and non-persistent members
to get shorter output:

    >>> browser.getControl('show docstrings').selected = False
    >>> browser.getControl('show all members').selected = False
    >>> browser.getControl('Update').click()
