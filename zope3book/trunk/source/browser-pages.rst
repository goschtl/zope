Browser Pages
=============

In the last chapter we have seen how to use resources HTML.  The
resource HTML will be only available on site-level with the `\@\@`
prefix.

Browser page (or more generically views) are representations for
particular objects/components.

If you have a template like this (helloworld.pt)::

  Hello, World !

Here is how to register a page for IFolder interface::

  <browser:page
    name="helloworld.html"
    for="zope.app.folder.interfaces.IFolder"
    template="helloworld.pt"
    permission="zope.Public"
    /> 


View components
---------------

While templates display data view components are preparing data.
View components convert data to output formats also prepare related
data (meta-data).  Then, create TAL-friendly object structures (dicts
and lists).  View components know about: component for which the
representation is created (context) and request object holding all
`output media` information (request)


Implementation
~~~~~~~~~~~~~~

Normally view components are added inside `browser` package inside
your main package.  The organization of the browser code is really up
to you and the above examples are just the most basic rules of thumb.

Here is simple view defined::

  from zope.publisher.browser import BrowserPage
  from zope.app.folder import interfaces

  class HelloWorld(BrowserPage):

      def subFolderIds(self):
          for name, subobj in self.context.items():
              if interfaces.IFolder.providedBy(subobj):
                  yield name 

Since methods and attributes of the view component are directly used
by the template, they should return simple iterable objects
(e.g. lists, tuples, generators) or mappings (e.g. dicts).


View components - integration
-----------------------------
