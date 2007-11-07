======
README
======

This package contains the trusted layer. This layer support a correct set of
component registration and can be used for inheritation in custom skins.

The ITrustedBrowserLayer supports the same registration set like the
IMinimalBrowserLayer. The only difference is, that the trusted layer offers
trusted traversal adapters. This means a skin using this layer can traverse
over a PAU (pluggable IAuthentication utility) without to run into a
Unautorized exception.

For more information see also the README.txt in z3c.layer.minimal.


Testing
-------

For testing the ITrustedBrowserLayer we use the testing skin defined in the
tests package which uses the ITrustedBrowserLayer. This means, that our
testing skin provides also the views defined in the minimal package
and it's testing views defined in the minimal tests.

Login as manager first:

  >>> from zope.testbrowser.testing import Browser
  >>> manager = Browser()
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')

Check if we can access the public page.html view which is registred in the
ftesting.zcml file with our skin:

  >>> skinURL = 'http://localhost/++skin++TrustedTesting'
  >>> manager.open(skinURL + '/page.html')
  >>> manager.url
  'http://localhost/++skin++TrustedTesting/page.html'

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
