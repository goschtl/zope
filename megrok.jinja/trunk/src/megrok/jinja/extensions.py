##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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

from jinja2.utils import contextfunction

from zope.component import getUtility, getMultiAdapter
from zope.i18n.interfaces import ITranslationDomain
from zope.contentprovider.interfaces import IContentProvider

class DomainNotDefined(Exception):
    def __str__(self):
        return """
    Domain translations it's required.
    Use {% set i18n_domain='your-domain' %} in the top of your template."""

@contextfunction
def _translator_alias(context, msgid, domain=None, mapping=None, ctx=None,
                      target_language=None, default=None):

    return context.resolve('gettext')(context, msgid, domain, mapping, ctx,
                                      target_language, default)

@contextfunction
def translator(context, msg, domain=None, mapping=None, ctx=None,
               target_language=None, default=None):

    ctx = ctx or context.resolve('view').request
    domain = domain or context.resolve('i18n_domain')
    if not domain:
        raise DomainNotDefined

    utility = getUtility(ITranslationDomain, domain)
    return utility.translate(msg,
                             mapping=mapping,
                             context=ctx,
                             target_language=target_language,
                             default=default)

@contextfunction
def _get_content_provider(context, name):
    view = context.resolve('view')

    provider = getMultiAdapter((view.context, view.request, view),
                                IContentProvider,
                                name=name)
    provider.update()
    return provider.render()
