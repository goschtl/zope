
:doctest:
:layer: grokui.codebrowser.tests.GrokCodeBrowserFunctionalLayer

We start a testbrowser to browse local code:

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.handleErrors = True

When browsing the root folder, we will be redirected to the code
browser, which is part of the grok UI framework:

    >>> browser.open('http://localhost/')
    >>> browser.url
    'http://localhost/++grokui++/@@codebrowser'

There is a link available, that will always bring us back to the ZODB
browsers root:

    >>> browser.getLink('Code browser')
    <Link text='Code browser' url='http://localhost/++grokui++/codebrowser'>

The codebrowser main screen provides an alphabetically sorted
selection of top-level packages to browse. Also the ``zope``,
``grokcore``, and ``grokui`` namespaces will be available. We browse
some parts of ``grokui.codebrowser``:

    >>> print browser.contents
    <html xmlns="http://www.w3.org/1999/xhtml">
    ...
    <a href="http://localhost/++grokui++/codebrowser/code/grokui">grokui</a>
    ...

As we can see, a certain dotted name can be reached via an URL like::

  http://localhost/++grokui++/codebrowser/code/DOTTED/NAME/OF/CODE

where the dotted name is in fact a 'slashed name'. For instance, to
browse the ``grokui.codebrowser`` package we use::

  http://localhost/++grokui++/codebrowser/code/grokui/codebrowser

Opening this screen we will see contained text files, ZCML files,
subpackages, modules, and more infos:

    >>> browser.open(
    ...  'http://localhost/++grokui++/codebrowser/code/grokui/codebrowser')
    >>> print browser.contents
    <html xmlns="http://www.w3.org/1999/xhtml">
    ...
    Contained text files:
    ...
    Contained ZCML files:
    ...
    Contained subpackages:
    ...
    Contained modules:
    ...

