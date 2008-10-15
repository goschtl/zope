five.megrok.z3cpt
=================

five.megrok.z3cpt bring z3c.pt web templates in the Grok world of Zope 2.

You can associate your template either directly in your code::

   from five import grok
   from five.megrok import z3cpt

   class Index(grok.View):
       pass

   index = z3cpt.PageTemplate("""Your template code""")

You are able to specify a filename as well:

   index = z3cpt.PageTemplate(filename="template.zpt")

You are able to creating a template with the extension ``.zpt`` in
your associated templates directory of your current module.

