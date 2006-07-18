=========
ZSCP Site
=========

Let's setup a ZSCP site:

  >>> from zf.zscp.website.site import ZSCPSite
  >>> zscp = ZSCPSite()

  # Add the site to the root, so it is fully located.
  >>> root = getRootFolder()
  >>> root[u'zscp'] = zscp

The object added event will normaly add the authentication utility:

  >>> from zope.app.component import hooks
  >>> hooks.setSite(zscp)

we can get the authentication utility with a simple lookup:

  >>> import zope.component
  >>> from zope.app import security
  >>> auth = zope.component.getUtility(security.interfaces.IAuthentication)

Since this authentication utility is a pluggable authentication utility, we
can ask it for all its authenticator plugins.

  >>> sorted(auth.getAuthenticatorPlugins())
  [(u'principals', <...principalfolder.PrincipalFolder ...>)]
