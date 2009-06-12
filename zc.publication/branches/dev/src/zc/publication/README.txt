Introduction
============

zc.publication.publcation is a publication object that extends
``zope.app.publication.browser.BrowserPublication`` with the ability
to provide an alternative root object, rather than one read from a
ZODB database.

Let's look at an example::


   import zope.publisher.browser

   class Hello(zope.publisher.browser.BrowserPage):

       def __init__(self, request):
           self.request = request

       def __call__(self):
           return """<html><body>
           Hello world
           </body></html>
           """

We'll put the code above in a module, ``hello``.

We also create a paste configuration file::

    [app:main]
    use = egg:zope.publisher
    publication = egg:zc.publication
    root = hello:Hello
    zcml = hello.zcml

Here, we:

- Use the ``zope.publisher`` WSGI application designed to work with paste.

- Use the ``zc.publication`` publication plugin for zope.publisher

- We specify a callable that takes a request and returns an object. In
  this case, we specify the Hello class.

- We specify the name of a ZCML file to be read to establish
  application configuration settings.

With these settings, we can access the URL::

   http://localhost/

and get the response::

   <html><body>
           Hello world
           </body></html>

