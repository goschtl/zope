##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Pluggable Authentication Utility Interfaces

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

class IPAUPrincipalCreated(zope.interface.Interface):
    """A PAU principal object has been created

    This event is generated when a transient PAU principal has been created.
    """

    principal = zope.interface.Attribute("The principal that was created")

    info = zope.schema.Dict(
          title=u"Supplemental Information",
          description=(
          u"Supplemental information returned from authenticator and search\n"
          u"plugins\n"
          ),
        )

class IAuthenticatedPrincipalCreated(IPAUPrincipalCreated):
    """An authenticated principal object has been created

    This event is generated when a principal has been created by
    authenticating a request.
    """

    request = zope.interface.Attribute(
        "The request the user was authenticated against")


class AuthenticatedPrincipalCreated:

    zope.interface.implements(IAuthenticatedPrincipalCreated)

    def __init__(self, principal, info, request):
        self.principal = principal
        self.info = info
        self.request = request

class IFoundPrincipalCreated(IPAUPrincipalCreated):
    """Event indicating that a principal was created based on a search
    """

class FoundPrincipalCreated:

    zope.interface.implements(IFoundPrincipalCreated)

    def __init__(self, principal, info):
        self.principal = principal
        self.info = info

class IPlugin(zope.interface.Interface):
    """Provide functionality to be pluged into a PAU
    """

class IPrincipalIdAwarePlugin(IPlugin):
    """Principal-Id aware plugin

    A requirements of plugins that deal with principal ids is that
    principal ids must be unique within a PAU.  A PAU manager may want
    to use plugins to support multiple principal sources.  If the ids
    from the various principal sources overlap, there needs to be some
    way to disambiguate them.  For this reason, it's a good idea for
    id-aware plugins to provide a way for a PAU manager to configure
    an id prefix or some other mechanism to make sure that
    principal-ids from different domains don't overlap.
    """

class IExtractionPlugin(IPlugin):
    """Extracts authentication credentials from a request.
    """

    def extractCredentials(request):
        """Try to extract credentials from a request

        A return value of None indicates that no credentials could be
        found. Any other return value is treated as valid credentials.
        """

class IAuthenticationPlugin(IPrincipalIdAwarePlugin):
    """Authenticate credentials
    """

    def authenticateCredentials(credentials):
        """Authenticate credentials

        If the credentials can be authenticated, return a 2-tuple with
        a principal id and a dictionary containing supplemental
        information, if any.  Otherwise, return None.
        """

class IChallengePlugin(IPlugin):
    """Initiate a challenge to the user to provide credentials.
    """

    protocol = zope.interface.Attribute("""Optional Challenger protocol

    If a challenger works with other challenger pluggins, then it and
    the other cooperating plugins should specify a common (non-None)
    protocol.  If a challenger returns True, then other challengers
    will be called only if they have the same protocol.
    """)

    def challenge(request, response):
        """Possibly issue a challenge

        This is typically done in a protocol-specific way.

        If a challenge was issued, return True. (Return False otherwise).
        """

class IPrincipalFactoryPlugin(IPlugin):
    """Create a principal object
    """

    def createAuthenticatedPrincipal(principal_id, info, request):
        """Create a principal authenticated against a request

        The info argument is a dictionary containing supplemental
        information that can be used by the factory and by event
        subscribers.  The contents of the info dictionary are defined
        by the authentication plugin used to authenticate the
        principal id.

        If a principal is created, an IAuthenticatedPrincipalCreated
        event must be published and the principal is returned.  If no
        principal is created, return None.
        """

    def createFoundPrincipal(user_id, info):
        """Return a principal, if possible.

        The info argument is a dictionary containing supplemental
        information that can be used by the factory and by event
        subscribers.  The contents of the info dictionary are defined
        by the search plugin used to find the principal id.

        If a principal is created, an IFoundPrincipalCreated
        event must be published and the principal is returned.  If no
        principal is created, return None.
        """

class IPrincipalSearchPlugin(IPrincipalIdAwarePlugin):
    """Find principals

    Principal search plugins provide two functions:

    - Get principal information, given a principal id

    - Search for principal ids

      Searching is provided in one of two ways:

      - by implementing `IQuerySchemaSearch`, or

      - by providing user interface components that support searching.
        (See README.txt.)
    """

    def principalInfo(principal_id):
        """Try to get principal information for the principal id.

        If the principal id is valid, then return a dictionary
        containing supplemental information, if any.  Otherwise,
        return None.
        """

class IQuerySchemaSearch(IPrincipalSearchPlugin):
    """
    """

    schema = zope.interface.Attribute("""Search Schema

    A schema specifying search parameters.
    """)

    def search(query, start=None, batch_size=None):
        """Search for principals

        The query argument is a mapping object with items defined by
        the plugins.  An iterable of principal ids should be returned.

        If the start argument is provided, then it should be an
        integer and the given number of initial items should be
        skipped.

        If the batch_size argument is provided, then it should be an
        integer and no more than the given number of items should be
        returned.
        """

class ISearchableAuthenticationPlugin(IAuthenticationPlugin,
                                      IPrincipalSearchPlugin):
    """Components that provide authentication ans searching

    This interface exists to make component registration a little bit easier.
    """

class IExtractionAndChallengePlugin(IExtractionPlugin, IChallengePlugin):
    """Components that provide credential extraction and challenge

    This interface exists to make component registration a little bit easier.
    """
    
