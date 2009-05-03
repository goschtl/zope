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

"""
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.component import getMultiAdapter

Let's create a request instance asking for Spanish translations.
We will set HTTP_ACCEPT_LANGUAGE to get the target_language. But
note that the extension adapts the request instance to
IUserPreferredLanguages. So, it's ok if you override this adapter
to get the language from a cookie or whatever.::

  >>> request = TestRequest(HTTP_ACCEPT_LANGUAGE = 'es')
  >>> context = Context()

Let's try the BreakLinesTranslate view. As we use the {% trans %} tag
it's important to note that the break lines (\n) counts.
If we use break lines in the tag body, the msgid in our
.po file must use the same break lines.::

  >>> view = getMultiAdapter((context, request), name='transtagtranslate')
  >>> print view()
  <BLANKLINE>
  Probando la extension i18n en megrok.jinja.
  Aca estamos usando la etiquera `trans`, por eso los saltos de linea.
  <BLANKLINE>
  <BLANKLINE>
  Probando el tag `trans` de i18n sin saltos de linea.

Most of the times it will be more comfortable to use the `_` function
with some short msgid::

  >>> view = getMultiAdapter((context, request), name='underscoretranslate')
  >>> print view()
  <BLANKLINE>
  <BLANKLINE>
  Probando la extension i18n en megrok.jinja usando la funcion `_`
  <BLANKLINE>
  Probando la extension i18n en megrok.jinja usando la funcion `_`

If we don't use {% set i18n_domain='some-domain' %} at the top
of our template, an exception it's raised::

  >>> view = getMultiAdapter((context, request), name='nodomain')
  >>> print view()
  Traceback (most recent call last):
     ...
  DomainNotDefined:
      Domain translations it's required.
      Use {% set i18n_domain='your-domain' %} in the top of your template.

When using `_` alias translator, we could use all the parameters in
zope.i18n.interfaces.ITranslationDomain.translate

  >>> view = getMultiAdapter((context, request), name='usingparams')
  >>> print view()
  Probando el mapeo con algo
"""


from grokcore.component import Context, context
from grokcore.view import View

class Context(Context):
    pass

class TransTagTranslate(View):
    context(Context)

class UnderscoreTranslate(View):
    context(Context)

    def update(self):
        self.msg = 'testing-underscore'

class NoDomain(View):
    context(Context)

class UsingParams(View):
    context(Context)

    def update(self):
        self.domain = 'test_domain'
        self.mapping = {'something' : 'algo'}

