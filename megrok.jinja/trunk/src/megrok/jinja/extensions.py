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

from jinja2 import nodes
from jinja2.ext import Extension, InternationalizationExtension
from jinja2.utils import contextfunction

from zope.component import getUtility, getMultiAdapter
from zope.i18n.interfaces import ITranslationDomain
from zope.contentprovider.interfaces import IContentProvider
from zope.cachedescriptors import method

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

class i18nExtension(InternationalizationExtension):
    """
    Jinja2 extension based on the `InternationalizationExtension`
    extension from jinja2.ext.
    """
    # We use the same tag that InternationalizationExtension
    # in order to be able to reuse the parser method
    tags = set(['trans'])

    def __init__(self, environment):
        Extension.__init__(self, environment)
        environment.globals['_'] = _translator_alias
        environment.extend(
            install_gettext_translations=self._install,
            install_null_translations=self._install_null,
            uninstall_gettext_translations=self._uninstall,
            extract_translations=self._extract
        )

    def _install(self):
        """
        We override this method to use a different translator
        allowing dynamic domains using zope.i18n machinery.
        """
        self.environment.globals.update(gettext=self.translator)

    @method.cachedIn('_cache')
    def trans_domain(self, domain):
        """
        Domains names are cached in order to avoid
        the getUtility call for each translation in the template.
        """
        return getUtility(ITranslationDomain, domain)

    @contextfunction
    def translator(self, context, msg, domain=None, mapping=None, ctx=None,
                   target_language=None, default=None):

        ctx = ctx or context.resolve('view').request
        domain = domain or context.resolve('i18n_domain')
        if not domain:
            raise DomainNotDefined

        return self.trans_domain(domain).translate(msg,
                                                   mapping=mapping,
                                                   context=ctx,
                                                   target_language=target_language,
                                                   default=default)

    def _make_node(self, singular, plural, variables, plural_expr):
        """
        This method it's called from the `parser` defined in
        `jinja2.ext.InternationalizationExtension` class.

        We need to override this method to handle the pluralize tag.
        """

        # singular only:
        if plural_expr is None:
            gettext = nodes.Name('gettext', 'load')
            node = nodes.Call(gettext, [nodes.Const(singular)],
                              [], None, None)

        # singular and plural
        else:
            #TODO: implement {%pluralize%} tag.
            raise NotImplementedError("{% pluralize %} was not implemented yet")

        # mark the return value as safe if we are in an
        # environment with autoescaping turned on
        if self.environment.autoescape:
            node = nodes.MarkSafe(node)

        if variables:
            node = nodes.Mod(node, variables)
        return nodes.Output([node])

class ContentProviderExtension(Extension):
    """
    Jinja2 extension to support the use of viewlets (content
    providers).

    It doesn't define any `tag`, just set the `provider` function name
    in the `Environment.globals`
    """
    def __init__(self, environment):
        Extension.__init__(self, environment)
        environment.globals['provider'] = self._get_content_provider

    @contextfunction
    def _get_content_provider(self, context, name):
        view = context.resolve('view')

        provider = getMultiAdapter((view.context, view.request, view),
                                    IContentProvider,
                                    name=name)
        provider.update()
        return provider.render()
