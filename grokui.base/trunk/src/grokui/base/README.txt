Detailed Description
********************

.. :doctest:
.. :layer: grokui.base.tests.test_grokuibase.FunctionalLayer

To build a component usable in the `grokui` environment we can (and
should) use viewlets, layouts, namespaces and menus from this
`grokui.base` package.

The ``++grokui++`` namespace
============================

In order not to pollute the default namespace of root folders too
much, all Grok UI related views should be kept in the ``++grokui++``
namespace which is defined and registered in `grokui.base`.

We can build a simple admin screen that fits into the environment like
this:

    >>> import grok
    >>> from zope.interface import Interface
    >>> from grokui.base import GrokUILayer

    >>> class MyAdminScreen(grok.View):
    ...   grok.layer(GrokUILayer)
    ...   grok.name('helloadmin')
    ...   grok.context(Interface)
    ...   def render(self):
    ...     return u'Hello admin!'

The important thing here is, that we set our view to belong to the
GrokUI namespace, which is named ``++grokui++`` in URLs.

We grok this view to register it with the component architechture:

    >>> grok.testing.grok_component('MyAdminScreen', MyAdminScreen)
    True

Let's create a browser to lookup this view:

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.handleErrors = False

We can get this screen when we ask for the correct namespace:

    >>> browser.open('http://localhost/++grokui++/@@helloadmin')
    >>> print browser.contents
    Hello admin!

If we ask for this view without the namespace set correctly, the view
will not be found:

    >>> browser.open('http://localhost/@@helloadmin')
    Traceback (most recent call last):
    ...
    NotFound: Object: <zope....Folder object at 0x...>, name: u'@@helloadmin'
