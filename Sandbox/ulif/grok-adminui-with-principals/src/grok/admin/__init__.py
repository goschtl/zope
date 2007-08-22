##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Initialize grok admin application.

The grok admin application provides a session based login, which
eventually must be enabled using Pluggable Authentication
Utilities. This is done here.
"""

from zope.component import adapter, provideHandler
from zope.app.appsetup.interfaces import IDatabaseOpenedWithRootEvent
from zope.app.authentication import PluggableAuthentication
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.security.interfaces import IAuthentication

from auth import PrincipalRegistryAuthenticator

AUTH_FOLDERNAME=u'authentication'
USERFOLDER_NAME=u'Users'
USERFOLDER_PREFIX=u'grokadmin'


def setupSessionAuthentication(root_folder=None,
                               fallback_only=False,
                               auth_foldername=AUTH_FOLDERNAME,
                               userfolder_name = USERFOLDER_NAME,
                               userfolder_prefix=USERFOLDER_PREFIX):
    """Add session authentication PAU to root_folder.

    Add a PluggableAuthentication in site manager of
    root_folder. ``auth_foldername`` gives the name of the PAU to
    install, userfolder_prefix the prefix of the authenticator plugin
    (a ``GrokAuthenticator``), which will be created in the PAU
    and gets name ``userfolder_name``.
    """
    sm = root_folder.getSiteManager()
    if (auth_foldername in sm.keys()
        and userfolder_name in sm[auth_foldername].keys()
        and isinstance(sm[auth_foldername][userfolder_name],
                          PrincipalFolder)):
        # Correct PAU already installed.
        return
    
    # Remove old PAU
    sm.unregisterUtility(name=u'', provided=IAuthentication)
    sm.unregisterUtility(name=USERFOLDER_NAME,
                                       provided=IAuthenticatorPlugin)
    sm.unregisterUtility(name='registry_principals',
                                       provided=IAuthenticatorPlugin)
    try:
        del sm[auth_foldername]
    except:
        pass

    pau = PluggableAuthentication()
    users = PrincipalFolder(userfolder_prefix)
    registry_users = PrincipalRegistryAuthenticator()
    registry_users.__name__ = u'registry_principals'

    # Configure the PAU...
    if fallback_only:
        pau.authenticatorPlugins = ('registry_principals')
    else:
        pau.authenticatorPlugins = (userfolder_name, 'registry_principals')
    pau.credentialsPlugins = ("No Challenge if Authenticated",
                              "Session Credentials")

    # Add the pau and its plugin to the root_folder...
    sm[auth_foldername] = pau
    sm[auth_foldername][userfolder_name] = users

    # Register the PAU with the site...
    sm.registerUtility(pau, IAuthentication)
    if not fallback_only:
        sm.registerUtility(users, IAuthenticatorPlugin, name=userfolder_name)
    sm.registerUtility(registry_users, IAuthenticatorPlugin,
                       name='registry_principals')


# If a new database is created, initialize a session based
# authentication.
#
# First create an eventhandler `adminSetup`, that is
# called, whenever a database is opened...
@adapter(IDatabaseOpenedWithRootEvent)
def adminSetup(event):
    from zope.app.appsetup.bootstrap import getInformationFromEvent
    
    db, connection, root, root_folder = getInformationFromEvent(event)
    setupSessionAuthentication(root_folder = root_folder)

# ...then install the event handler:
provideHandler(adminSetup)

