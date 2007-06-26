========================
HTTP-Referer Credentials
========================

It is sometimes necessary to restrict access to a site by looking at the the
site the user is coming from. For example, a user can only enter the site when
he comes from within the corporate network. If the two sites cannot share any
specific information, such as an authentication token, the only useful piece
of information is the ``HTTP-Referer`` request header.

__Note__: Yes I know this is not fully secure and someone could spoof the
header. But this is acceptable in this particular application. I guess it
keeps away the honest. And yes, this is a real world scenario -- would I
implement this package otherwise? :-)

So let's have a look at the credentials plugin:

  >>> from z3c.referercredentials import credentials
  >>> creds = credentials.HTTPRefererCredentials()

Let's look at the positive case first. The referer credentials plugin has an
attribute that specifies all allowed hosts:

  >>> creds.allowedHosts
  ('localhost',)

In this example, we only want to allow peopl eto the site coming from
``www.zope.org``.

  >>> creds.allowedHosts = ('www.zope.org',)

Now, a user coming from that site will have a request containing this referer:

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest(HTTP_REFERER='http://www.zope.org/index.html')

The credentials can now be extracted as follows:

  >>> creds.extractCredentials(request)

Nothing is returned. This is because we have not defined any credentials that
represent the "referer user". With setting the credentials, it should work:

  >>> creds.credentials = {'login': 'mgr', 'password': 'mgrpw'}
  >>> creds.extractCredentials(request)
  {'login': 'mgr', 'password': 'mgrpw'}

Once an acceptable referer has been passed in, the credentials are always
returned:

  >>> del request._environ['HTTP_REFERER']
  >>> creds.extractCredentials(request)
  {'login': 'mgr', 'password': 'mgrpw'}

We have to log out in order to loose the credentials:

  >>> creds.logout(request)
  True

Now, no credentials are returned when not sending in a correct referer:

  >>> creds.extractCredentials(request)

When the user could not be authenticated, the plugin is asked to pose a
challenge:

  >>> creds.challenge(request)
  True
  >>> request.response.getHeader('Redirect')

By default we are getting the "unauthorized.html" view on the site. But you
can change the view name:

  >>> creds.challengeView = 'challenge.html'
  >>> creds.challenge(request)
  True
  >>> request.response.getHeader('Redirect')

Final Note: Of course, this credentials plugin only works with HTTP-based
requests:

  >>> request = object()

  >>> creds.extractCredentials(request)

  >>> creds.challenge(request)
  False

  >>> creds.logout(request)
  False
