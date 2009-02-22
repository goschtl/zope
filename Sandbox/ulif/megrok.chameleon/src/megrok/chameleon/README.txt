Detailed Description
********************

Grok-support for using chameleon driven templates.

:Test-Layer: functional

With `megrok.chameleon` you can use templates parsed and rendered by
`chameleon`. Currently Zope page templates and Genshi templates are
supported.

Chameleon Zope page templates
=============================

Chameleon provides support for Zope page templates which can be used
from grok writing templates with the ``.cpt`` (=Chameleon Page
Template) filename extension.

Chameleon page templates differ from standard Zope page templates in a
few aspects, most notably:

* Expressions are parsed in ``Python-mode`` by default. This means,
  instead of ``tal:content="view/value"`` you must use
  ``tal:content="view.value"``. Every occurence of TAL-expressions
  starting with ``python:`` now can be shortened by skipping this
  marker.

* Also genshi-like variable substitutions are supported. For example
  you can write ``${myvar}`` instead of ``tal:content="myvar"``.

Beside this, most rules for regular Zope page templates apply also to
chameleon page templates.

See the `chameleon.zpt`_ page for more information.

.. _chameleon.zpt: http://pypi.python.org/pypi/chameleon.zpt

Prerequisites
-------------

Before we can see the templates in action, we care for correct
registration and set some used variables::

    >>> import os
    >>> testdir = os.path.join(os.path.dirname(__file__), 'tests')
    >>> cpt_fixture = os.path.join(testdir, 'cpt_fixture')
    >>> template_dir = os.path.join(cpt_fixture, 'app_templates')

We register everything. Before we can grok our fixture, we have to
grok the `megrok.chameleon` package. This way the new template types
are registered with the framework::

    >>> import grok
    >>> grok.testing.grok('megrok.chameleon')
    >>> grok.testing.grok('megrok.chameleon.tests.cpt_fixture')

We create a mammoth, which should provide us a bunch of chameleon page
template driven views and put it in the database to setup location
info::

    >>> from megrok.chameleon.tests.cpt_fixture.app import Mammoth
    >>> manfred = Mammoth()
    >>> getRootFolder()['manfred'] = manfred

Furthermore we prepare for getting the different views on manfred::

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.component import getMultiAdapter
    >>> request = TestRequest()

Simple templates
----------------

We prepared a plain cavepainting view. The template looks like this::

    >>> cavepainting_cpt = os.path.join(template_dir, 'cavepainting.cpt')
    >>> print open(cavepainting_cpt, 'rb').read()
    <html>
      <body>
        A cave painting.
      </body>
    </html>

The rendered view looks like this::

    >>> view = getMultiAdapter((manfred, request),
    ...                         name='cavepainting')
    >>> print view()
    <html>
      <body>
        A cave painting.
      </body>
    </html>

Substituting variables
----------------------

A template can access variables like ``view``, ``context`` and its
methods and attributes. The ``food`` view does exactly this. The
template looks like this::

    >>> food_cpt = os.path.join(template_dir, 'food.cpt')
    >>> print open(food_cpt, 'rb').read()
    <html>
    <body>
    <span tal:define="foo 'a FOO'" />
    ${view.me_do()}
    CSS-URL: ${static['test.css']()}
    My context is: ${view.url(context)}
    ${foo}
    </body>
    </html>

The rendered view looks like this::

    >>> view = getMultiAdapter((manfred, request), name='food')
    >>> print view()
    <html>
    <body>
    <span />
    ME GROK EAT MAMMOTH!
    CSS-URL: http://127.0.0.1/@@/megrok.chameleon.tests.cpt_fixture/test.css
    My context is: http://127.0.0.1/manfred
    a FOO
    </body>
    </html>

Inline Templates
----------------

We can also define inline templates. In our ``app.py`` we defined an
inline template like this::

  import grok
  from megrok.chameleon import components

  ...

  class Inline(grok.View):
    sometext = 'Some Text'

  inline = components.ChameleonPageTemplate(
      "<html><body>ME GROK HAS INLINES! ${view.sometext}</body></html>")

If we render this view we get::

    >>> view = getMultiAdapter((manfred, request), name='inline')
    >>> print view()
    <html><body>ME GROK HAS INLINES! Some Text</body></html>

Clean up::

    >>> del getRootFolder()['manfred']


Chameleon Genshi templates
==========================

Chameleon provides supprt for Genshi templates which can be used from
grok writing templates with the ``.cg`` filename extension.

Genshi text templates can be used with the ``.cgt`` filename
extension.

Note, that chameleon genshi templates might not cover the full range
of functionality offered by native genshi parsers. Use `megrok.genshi`
if you want native genshi support.

See the `chameleon.genshi`_ page for more information.

.. _chameleon.genshi: http://pypi.python.org/pypi/chameleon.genshi


Prerequisites
-------------

Before we can see the templates in action, we care for correct
registration and set some used variables::

    >>> import os
    >>> testdir = os.path.join(os.path.dirname(__file__), 'tests')
    >>> genshi_fixture = os.path.join(testdir, 'genshi_fixture')
    >>> template_dir = os.path.join(genshi_fixture, 'app_templates')

We register everything. Before we can grok our fixture, we have to
grok the `megrok.chameleon` package. This way the new template types
are registered with the framework::

    >>> import grok
    >>> grok.testing.grok('megrok.chameleon')
    >>> grok.testing.grok('megrok.chameleon.tests.genshi_fixture')

We create a mammoth, which should provide us a bunch of Genshi driven
views and put it in the database to setup location info::

    >>> from megrok.chameleon.tests.genshi_fixture.app import Mammoth
    >>> manfred = Mammoth()
    >>> getRootFolder()['manfred'] = manfred

Furthermore we prepare for getting the different views on manfred::

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.component import getMultiAdapter
    >>> request = TestRequest()


Simple templates
----------------

We prepared a plain cavepainting view. The template looks like this::

    >>> cavepainting_cg = os.path.join(template_dir, 'cavepainting.cg')
    >>> print open(cavepainting_cg, 'rb').read()
    <html>
      <body>
        A cave painting.
      </body>
    </html>

The rendered view looks like this::

    >>> view = getMultiAdapter((manfred, request),
    ...                         name='cavepainting')
    >>> print view()
    <html>
      <body>
        A cave painting.
      </body>
    </html>


Substituting variables
----------------------

A template can access variables like ``view``, ``context`` and its
methods and attributes. The ``food`` view does exactly this. The
template looks like this::

    >>> food_cg = os.path.join(template_dir, 'food.cg')
    >>> print open(food_cg, 'rb').read()
    <html>
    <body>
    ${view.me_do()}
    CSS-URL: ${static['test.css']()}
    My context is: ${view.url(context)}
    </body>
    </html>

The rendered view looks like this::

    >>> view = getMultiAdapter((manfred, request), name='food')
    >>> print view()
    <html>
    <body>
    ME GROK EAT MAMMOTH!
    CSS-URL: http://127.0.0.1/@@/megrok.chameleon.tests.genshi_fixture/test.css
    My context is: http://127.0.0.1/manfred
    </body>
    </html>


Including other templates
-------------------------

With genshi support we can also include other templates. The
``gatherer`` view looks like this::

    >>> gatherer_cg = os.path.join(template_dir, 'gatherer.cg')
    >>> print open(gatherer_cg, 'rb').read()
    <html xmlns:xi="http://www.w3.org/2001/XInclude">
    <body>
    ME GROK GATHER BERRIES!
    <xi:include href="berries.cg"/>
    </body>
    </html>

Apparently here we include a template called ``berries.cg``. It looks
like this::

    >>> berries_cg = os.path.join(template_dir, 'berries.cg')
    >>> print open(berries_cg, 'rb').read()
    <strong>Lovely blueberries!</strong>


When we render the former template, we get::

    >>> view = getMultiAdapter((manfred, request), name='gatherer')
    >>> print view()
    <html>
    <body>
    ME GROK GATHER BERRIES!
    <strong>Lovely blueberries!</strong>
    </body>
    </html>

Text templates
--------------

Also genshi text templates are supported. We have a template that
looks like so::

    >>> hunter_cgt = os.path.join(template_dir, 'hunter.cgt')
    >>> print open(hunter_cgt, 'rb').read()
    ME GROK HUNT ${view.game}!

Note, that this template has the ``.cgt`` (= **c**\ ameleon **g**\ enshi
**t**\ ext template) file extension.

If we render it, all expressions are substituted::

    >>> view = getMultiAdapter((manfred, request), name='hunter')
    >>> print view()
    ME GROK HUNT MAMMOTH!!
