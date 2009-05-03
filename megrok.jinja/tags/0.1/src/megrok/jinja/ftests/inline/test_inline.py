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
  >>> request = TestRequest()
  >>> manfred = Mammoth()

Let's get our first view that should render a plain text extending macros.jinja.

  >>> view = getMultiAdapter((manfred, request), name='sayhi')
  >>> print view()
  Head content
  <BLANKLINE>
  GROK SAY HI!
  <BLANKLINE>
  Footer content

We may want to set variables to use in the template

  >>> view = getMultiAdapter((manfred, request), name='cavepainting')
  >>> view()
  u'GROK SAY: I LIKE BROWN COLOR'

Let's see what happen with JSON templates. In the template we use
YAML and Jinja2

  >>> view = getMultiAdapter((manfred, request), name='jsonview')
  >>> view()
  '{"dicts": [{"key1": "some_text"}, {"k2": "val2", "k1": "val1"}]}'

Note that the rendered text it's the result of simplejson.dumps
See YAML documentation to learn how to say what you want

"""


from grokcore.component import Context, context
from grokcore.view import View

from zope.interface import Interface
from megrok.jinja.factory import JinjaTemplate, JsonTemplate

import os

import megrok.jinja.ftests.inline as inline
templates = os.path.join(os.path.dirname(inline.__file__),
                         'test_inline_templates')

class Mammoth(Context):
    pass

class Macros(View):
    """
    Templates that define blocks to be
    extended must use a template file
    """
    context(Mammoth)

class SayHi(View):
    context(Mammoth)

    def update(self):
        self.macros_tpl = "%s/macros.jinja" % templates

sayhi = JinjaTemplate("""{% extends view.macros_tpl %}
{% block main %}
GROK SAY HI!
{% endblock %}
""")

class CavePainting(View):
    context(Mammoth)

    def update(self):
        self.color = 'BROWN'

cavepainting = JinjaTemplate("GROK SAY: I LIKE {{ view.color }} COLOR")

class JsonView(View):
    context(Mammoth)

    def update(self):
        self.dict = {'k1' : 'val1', 'k2' : 'val2'}

jsonview = JsonTemplate("""
dicts :
  - key1 : some_text
  - {{ view.dict }}
""")
