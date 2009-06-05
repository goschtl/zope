megrok.z3cpt
************

``megrok.z3cpt`` is an extension providing `z3c.pt`_ templates in Grok
and five.grok.

You can define a `z3c.pt`_ template by:

- Associating your template directly in your code::

    import grok
    from megrok import z3cpt

    class Index(grok.View):
        pass

    index = z3cpt.PageTemplate("""Your template code""")

- Specifying a file template::

   index = z3cpt.PageTemplate(filename="template.zpt")

- Creating your template with the extension ``.zpt`` in the
  associated templates directory of the current module.

Installation
============

You need to refer ``megrok.z3cpt`` as a dependency of your application
and to load the following ZCML::

  <include package="megrok.z3cpt" />

Note
----

`z3c.pt`_ require at least `zope.i18n`_ 3.5. You need to override in
your ``versions.cfg`` in order to prevent a conflict.

For Zope 2 user, you need to specify `zope.i18n`_ in
``skip-fake-eggs`` option of your Zope 2 installation.

.. _zope.i18n: http://pypi.python.org/pypi/zope.i18n
.. _z3c.pt: http://pypi.python.org/pypi/z3c.pt
