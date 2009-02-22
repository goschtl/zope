megrok.chameleon
****************

Grok-support for using chameleon driven templates.

:Test-Layer: functional

With `megrok.chameleon` you can use templates parsed and rendered by
`chameleon`. Currently Zope page templates and Genshi templates are
supported.

Chameleon Zope page templates
=============================


Chameleon Genshi templates
==========================

Chameleon provides supprt for Genshi templates which can be used from
grok writing templates with the ``.cg`` filename extension.

Genshi text templates can be used with the ``.cgt`` filename
extension.

Note, that chameleon genshi templates might not cover the full range
of functionality offered by native genshi parsers. Use `megrok.genshi`
if you want native genshi support.

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

Note, that this template has the ``.cgt`` (= **c**ameleon **g**genshi
**t**ext template) file extension.

If we render it, all expressions are substituted::

    >>> view = getMultiAdapter((manfred, request), name='hunter')
    >>> print view()
    ME GROK HUNT MAMMOTH!!
