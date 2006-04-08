=========
ZSCP Site
=========

Let's setup a ZSCP site:

  >>> from zf.zscp.website import zscp
  >>> zscp = zscp.ZSCPSite()

  # Add the site to the root, so it is fully located.
  >>> from zope.app.folder import rootFolder
  >>> root = rootFolder()
  >>> root[u'zscp'] = zscp

  >>> from zf.zscp.website.zscp import addAuthenticationUtilityToSite
  >>> addAuthenticationUtilityToSite(zscp, None)

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
