======
README
======

This package contains the minimal layer. This layer supports a correct set of 
component registration and can be used for inheritance in custom skins.

Right now the default implementation in Zope3 has different restrictions in the
traversal concept and use to many registrations on the default layer.


IMinimalBrowserLayer
--------------------

The minimal layer is useful for build custom presentation skins without access 
to ZMI menus like zmi_views etc. This means there is no menu item registered if 
you use this layer.

This layer is NOT derived from IDefaultBrowserLayer. Therefore it provides 
only a minimal set of the most important public views such as @@absolute_url. 
The following packages are accounted:

- zope.app.http.exception
- zope.app.publication
- zope.app.publisher.browser
- zope.app.traversing
- zope.app.traversing.browser


Testing
-------

For testing the IMinimalBrowserLayer we use the testing skin defined in the 
tests package which uses the IMinimalBrowserLayer as the only base layer.
This means, that our testing skin provides only the views defined in the 
minimal package and it's testing views defined in tests.

Login as manager first:

  >>> from zope.testbrowser.testing import Browser
  >>> manager = Browser()
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')

Check if we can access the page.html view which is registred in the 
ftesting.zcml file with our skin:

  >>> manager = Browser()
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> skinURL = 'http://localhost/++skin++MinimalTesting'
  >>> manager.open(skinURL + '/page.html')
  >>> manager.url
  'http://localhost/++skin++MinimalTesting/page.html'

  >>> print manager.contents
  <BLANKLINE>
  <html>
  <head>
    <title>testing</title>
  </head>
  <body>
  <BLANKLINE>
    test page
  <BLANKLINE>
  </body>
  </html>
  <BLANKLINE>
  <BLANKLINE>

Now check the not found page which is a exception view on the exception
``zope.publisher.interfaces.INotFound``:

  >>> manager.open(skinURL + '/foobar.html')
  Traceback (most recent call last):
  ...
  HTTPError: HTTP Error 404: Not Found

  >>> print manager.contents
  <BLANKLINE>
  <html>
  <head>
    <title>testing</title>
  </head>
  <body>
  <div>
    <br />
    <br />
    <h3>
      The page you are trying to access is not available
    </h3>
    <br />
    <b>
      Please try the following:
    </b>
    <br />
    <ol>
      <li>
        Make sure that the Web site address is spelled correctly.
      </li>
      <li>
        <a href="javascript:history.back(1);">
          Go back and try another URL.
        </a>
      </li>
    </ol>
  </div>
  </body>
  </html>
  <BLANKLINE>
  <BLANKLINE>

And check the user error page which is a view registred for 
``zope.exceptions.interfaces.IUserError`` exceptions:

  >>> manager.open(skinURL + '/@@usererror.html')
  >>> print manager.contents
  <BLANKLINE>
  <html>
  <head>
    <title>testing</title>
  </head>
  <body>
  <div>
    <div>simply user error</div>
  </div>
  </body>
  </html>
  <BLANKLINE>
  <BLANKLINE>

And check error view registred for 
``zope.interface.common.interfaces.IException``:

  >>> manager.open(skinURL + '/@@systemerror.html')
  >>> print manager.contents
  <BLANKLINE>
  <html>
  <head>
    <title>testing</title>
  </head>
  <body>
  <div>
    <br />
    <br />
    <h3>A system error occurred</h3>
    <br />
    <b>Please contact the administrator.</b>
    <a href="javascript:history.back(1);">
      Go back and try another URL.
    </a>
  </div>
  </body>
  </html>
  <BLANKLINE>
  <BLANKLINE>

And check the ``zope.security.interfaces.IUnauthorized`` view, use a new 
unregistred user (test browser) for this:

  >>> unauthorized = Browser()
  >>> unauthorized.open(skinURL + '/@@forbidden.html')
  Traceback (most recent call last):
  ...
  HTTPError: HTTP Error 401: Unauthorized

  >>> print unauthorized.contents
  <BLANKLINE>
  <html>
  <head>
    <title>testing</title>
  </head>
  <body>
  <div>
  <BLANKLINE>
  <h1>Unauthorized</h1>
  <BLANKLINE>
  <p>You are not authorized</p>
  <BLANKLINE>
  </div>
  </body>
  </html>
  <BLANKLINE>
  <BLANKLINE>
