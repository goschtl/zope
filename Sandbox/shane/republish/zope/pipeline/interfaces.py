##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""Interfaces specific to zope.pipeline.

$Id: metadirectives.py 96177 2009-02-06 07:50:13Z shane $
"""

from zope.interface import Attribute
from zope.interface import Interface

class IUndecidedRequest(Interface):
    """Indicates that no request has been created yet.

    Use this interface to register WSGI applications in the
    pipeline that executes before the request creation step.
    """

class IPipelineApplicationList(Interface):
    """Container of a list of pipeline application names.

    The wsgi:pipeline directive creates an object that
    provides this interface and registers it as an adapter.
    """
    names = Attribute("Application names to use in a pipeline")

class IRequestFactoryRegistry(Interface):
    """A registry of request factories.

    Chooses factories based on the wsgi.url_scheme, the
    REQUEST_METHOD, and the CONTENT_TYPE.  Multiple factories
    can be configured schema, method, and content type.
    The factory itself can introspect the environment to decide
    if it can handle the request as given by the environment or not.
    Factories are sorted in descending order of priority, so a
    factory with priority 10 will be used before a factory with
    priority 5.
    """

    def register(scheme, method, mimetype, name, priority, factory):
        """Registers a factory for scheme + method + mimetype."""

    def get_factories_for(scheme, method, mimetype):
        """Return the internal datastructure representing the configured
        factories (basically for testing, not for introspection).
        """

    def lookup(method, mimetype, environment):
        """Lookup a factory for a given method+mimetype and a
        environment.
        """
