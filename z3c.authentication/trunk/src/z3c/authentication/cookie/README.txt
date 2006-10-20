======
README
======

The target of this package is to offer a cookie based auto login.

This is what Zope3 can do by default with the session credential plugin. But
there is a restriction if you use the default implementation for doing this.
The Zope session credential plugin uses the same session data container for
the session credential and all other session datas which means if you 
configure this for a longtimeframe all other session data get store this long.

This package offers all components for separate the session credential data 
into a own session data container. This implementation offers also a 
configurator plugin which will configure a site wich a liftime session for you.

Let's import our SiteStub first:

  >>> from z3c.authentication.cookie.testing import ISiteStub
  >>> from z3c.authentication.cookie.testing import SiteStub  

Note, the configurator are allready setup which will make a site and add
the credential plugin. See z3c.authentication.cookie.testing for more info.

Now add the site,

  >>> import zope.event
  >>> import zope.lifecycleevent
  >>> siteStub = SiteStub()
  >>> zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(siteStub))
  >>> rootFolder['siteStub'] = siteStub
  >>> siteStub =  rootFolder['siteStub']

invoke the configurator, normaly done in the site add form,

  >>> from z3c.configurator import configurator
  >>> configurator.configure(siteStub, {})

and see what component we get added via the configurator plugin.

  >>> import zope.component
  >>> sm = zope.component.getSiteManager(siteStub)
  >>> default = sm['default']
  >>> tuple(default.keys())
  (u'CookieClientIdManager', u'CookieCredentialSessionDataContainer',...
  u'PluggableAuthentication')

Check if the PAU contains a liftime cookie session credential:

  >>> pau = default['PluggableAuthentication']
  >>> credential = pau['Z3C Cookie Credentials']
  >>> credential
  <z3c.authentication.cookie.plugin.CookieCredentialsPlugin object at ...>

And check if the PAU is correct configured for useing this plugin.

  >>> pau.credentialsPlugins
  (u'Z3C Cookie Credentials',)

We also need to check if we got a own CookieClientIdManager which the 
liftime is set to o (zero) whichmeans it never will expire.

  >>> ccim = default['CookieClientIdManager']
  >>> ccim.cookieLifetime
  0

The last part in the concept is the cookie session data container. This 
session storage has to provide a timeout of 0 (zero) which means it's item
the persistent CookieCredentials will never expire.

  >>> from z3c.authentication.cookie import interfaces
  >>> sdc = default['CookieCredentialSessionDataContainer']
  >>> sdc
  <z3c.authentication.cookie.session.CookieCredentialSessionDataContainer ...> 

Check if this container s also available as utility.

  >>> from zope.app.session.interfaces import ISessionDataContainer
  >>> ccsdc = zope.component.getUtility(ISessionDataContainer, 
  ...     name=interfaces.SESSION_KEY)
  >>> ccsdc
  <z3c.authentication.cookie.session.CookieCredentialSessionDataContainer ...>

  >>> ccsdc.timeout
  0