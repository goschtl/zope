MEGROK PAGELET
==============

This package try to bring the functionality of `z3c.template`_ and
`z3c.pagelet`_ to Grok.

`z3c.template`_ gives an alternative way to the ``zpt:metal`` layout
based system in Grok.  `z3c.pagelet`_ provides the possibility to
register layouts with the help of the zope component
architecture. This allows to separate the rendering of the layout and
the content.

This is implemented with the help of the ``megrok.pagelet.Layout``
component which holds the layout.

The Layout (Skin)
-----------------

The first thing we have to do is to define a layout::

  class MyLayout(megrok.pagelet.Layout):
      grok.context()
      grok.layer()

      megrok.pagelet.template('my_layout_template.pt')

The template ``my_layout_template.pt`` is registered as a layout for
the given context and layer. Of course it's possible to specify
different layouts for different layers or contexts.

In the content of ``my_layout_template.pt`` is something like this::

  <html>
    <body>
      <div class="layout" tal:content="structure view/render">
           here comes the content
      </div>
    </body>
  </html>

The Pagelet (View)
------------------

Instead of using the common ``grok.View`` for our views we use now
``megrok.pagelet.Paglet``. This component has one difference to a
normal view, it does not only return the rendered content of the
component, it first search for the layout in given context and layer
and then it renders the content in this layout::

  class View(megrok.pagelet.Pagelet)
      grok.context()
      grok.layer()
      grok.name()

      def render(self)
          return u"Something"


Now if you point your browser on ``.../view`` you sould see the
rendered view in the given layout.

.. _z3c.template: http://pypi.python.org/pypi/z3c.template
.. _z3c.pagelet: http://pypi.python.org/pypi/z3c.pagelet
