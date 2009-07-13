==================
z3c.hashedresource
==================

While we want browsers to cache static resources such as CSS-stylesheets and
JavaScript files, we also want them *not* to use the cached version if the
files on the server have been updated. (And we don't want to make end-users
have to empty their browser cache to get the latest version. Nor explain how
to do that over the phone every time.)

To make browsers update their caches of resources immediately when the
resource changes, the absolute URLs of resources can now be made to contain a
hash of the resource's contents, so it will look like
/++noop++12345/@@/myresource instead of /@@/myresource.

In developer mode the hash is recomputed each time the resource is asked for
its URL, while in production mode the hash is computed only once, so remember
to restart the server after changing resource files (else browsers will still
see the old URL unchanged and use their outdated cached versions of the files).

To use this package, include its configure.zcml and use
`z3c.hashedresource.interfaces.IHashedResourceSkin` or a skin that inherits from
it.

The dependency on zope.app.publisher >= 3.8.2 is not longer declared
explicitly in order to gain compatibility with Zope2, but it is still required
when using Zope3.
