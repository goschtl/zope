MEGROK PAGELET
==============

This package try to bring the functionality of z3c.template and
z3c.pagelet to grok.
 
z3c.template gives us a alternative for the zpt:metal layout based system in grok.
The z3c.pagelet has the advantage that it´s possible to register layouts with help of
the zope-component-architecuture this allows you to change or modify layouts 
without touching the *master* macro.

This means you have megrok.pagelet.Layout component which holds
the layout. Instead of using grok.View you have to take 
megrok.pagelet.Pagelet for normal BrowserViews.

If you need more information about z3c.template please look here [1].

The Layout
----------

The first thing we have to do is set up a layout for our pagelet.

class MyLayout(megrok.pagelet.Layout):
    grok.context()
    grok.layer()

    megrok.pagelet.template('my_layout_template.pt')

This configures the template ('my_layout_template.pt') as a layout for the given
context and layer. Of course it´s possible to specify different 
layouts for different layers or contexts.


In the content of my_layout_template.pt is something like this:

<html>
 <body>
   <div class="layout" tal:content="structure view/render">
         here comes the content
   </div>
 </body>
</html>

The Pagelt (View)
-----------------

Ok instead of using the common grok.View for our BrowserViews we use now
megrok.pagelet.Paglet. This component has one difference to a normal
grok.View. This difference is in the __call__ method of the megrok.pagelet.Pagelet.
This means that the  __call__ method of a  Pagelet does not only return the renderd 
"template" of the Pagelet. The __call__ first search for the layout in given context
and layer and  then it renders the "template" in this layout.

class View(megrok.pagelet.Pagelet)
    grok.context()
    grok.layer()
    grok.name()

    def render(self)
	return "..."


Now if you point your browser on .../view you sould see the renderd view in the
given layout.

[1] http://pypi.python.org/pypi/z3c.template/1.1.0
