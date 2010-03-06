
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
    <Link text='_sm' url='http://localhost/++grokui++/@@zodbbrowser/...>
