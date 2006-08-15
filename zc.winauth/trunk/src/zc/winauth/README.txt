======================
Windows Authentication
======================

This package provides for authenticating windows users with their domain
user names and passwords.

---------------------------
WindowsAuthenticationPlugin
---------------------------

The authentication is done via a WindowsAuthenticationPlugin:

    >>> from zc.winauth.winauth import WindowsAuthenticationPlugin
    >>> wap = WindowsAuthenticationPlugin()
  
When a user needs to be authenticated there credentials are passed to the
plugin:

    >>> credentials = {'login': 'jdoe', 'password': 'pass'}

The result of authentication is information about the principal:

    >>> info = wap.authenticateCredentials(credentials)
    >>> info is not None
    True

The IDs are constructed using Windows' SIDs:

    >>> info.id
    'zc.winauth.S-...'

They also have a title:

    >>> info.title
    u'John Doe'

If an unknown user name or incorrect password are given, None is returned:

    >>> badCredentials = {'login': 'jdoe', 'password': 'wrong'}
    >>> wap.authenticateCredentials(badCredentials) is None
    True

If the credentials are None, then None is returned:

    >>> print wap.authenticateCredentials(None)
    None


------
Prefix
------

The plugin uses a prefix for all principal IDs:

    >>> wap.prefix
    'zc.winauth'

If an ID is passed to principalInfo that doesn't have the right prefix, None is
returned:

    >>> print wap.principalInfo('different.prefix')
    None

-------------
Server Errors
-------------

If an error occurrs while checking a user's password, the credentials are
denied:

    >>> bool(wap.checkPassword('error', 'pass'))
    False

Something similar happens if an error occurrs while retrieving principal info:

    >>> print wap.principalInfo('zc.winauth.error')
    None

If the error is that the domain controller we're using is no longer available,
the result will be as if the user doesn't exist (dc_is_dead is just a knob for
testing).

    >>> win32net.dc_is_dead = True
    >>> print wap.authenticateCredentials(credentials)
    None
    >>> print wap.principalInfo('zc.winauth.jsmith')
    None
    >>> win32net.dc_is_dead = False

-------------
Missing Title
-------------

If a user has an empty "full_name", their user name will be used instead:

    >>> info = wap.principalInfo('zc.winauth.S-1-5-2')
    >>> info.title
    'jsmith'

-------------------------
Repeating bad credentials
-------------------------

In the face of bad credentials, authentication will only be attempted once
during a timeout period.  This is to resolve problems when a policy of locking
out accounts after a number of failed login attempts is in effect.

    >>> credentials = {'login': 'jdoe', 'password': 'pass'}
    >>> wap.authenticateCredentials(credentials) is not None
    True

If the credentials suddenly start failing...

    >>> win32security.all_logins_are_bad = True
    >>> wap.authenticateCredentials(credentials) is not None
    False

...they will continue to fail.

    >>> win32security.all_logins_are_bad = False
    >>> wap.authenticateCredentials(credentials) is not None
    False
    >>> wap.authenticateCredentials(credentials) is not None
    False

After a timeout, the credentials will work again.

    >>> import zc.winauth.winauth
    >>> original_timeout = zc.winauth.winauth.BAD_CREDENTIALS_TIMEOUT
    >>> zc.winauth.winauth.BAD_CREDENTIALS_TIMEOUT = 0
    >>> wap.authenticateCredentials(credentials) is not None
    True
    >>> zc.winauth.winauth.BAD_CREDENTIALS_TIMEOUT = original_timeout

It is common for credentials == None at some point *between* authentication of
the real credentials.  So, if again the credentials initially work...

    >>> credentials = {'login': 'jdoe', 'password': 'pass'}
    >>> wap.authenticateCredentials(credentials) is not None
    True

...and then suddenly start failing...

    >>> win32security.all_logins_are_bad = True
    >>> wap.authenticateCredentials(credentials) is not None
    False

...they will continue to fail, even if None credentials are tried between.

    >>> win32security.all_logins_are_bad = False
    >>> wap.authenticateCredentials(credentials) is not None
    False
    >>> wap.authenticateCredentials(None) is not None
    False
    >>> wap.authenticateCredentials(credentials) is not None
    False

After a timeout, the credentials will work again.

    >>> import zc.winauth.winauth
    >>> original_timeout = zc.winauth.winauth.BAD_CREDENTIALS_TIMEOUT
    >>> zc.winauth.winauth.BAD_CREDENTIALS_TIMEOUT = 0
    >>> wap.authenticateCredentials(credentials) is not None
    True

We need to set the timeout back.

    >>> zc.winauth.winauth.BAD_CREDENTIALS_TIMEOUT = original_timeout
