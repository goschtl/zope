========
Snippets
========

The idea of widget snippets is that often widgets will have some surrounding
HTML code, perhaps a label, outlining what e.g. an input field is for, some
code regarding error handling and perhaps some simple formatting.

For instance, a widget may render as:

<input type="text" value="" />

But in the resulting HTML page, we need some surrounding code, e.g.

<div>
MyWidget: <input type="text" value="" />
</div>

Widget Snippets allow designers to create custom snippets and register them
for certain widgets and display modes. 

First we have to register the meta configuration for the directive.

  >>> import zope,sys
  >>> from zope.configuration import xmlconfig
  >>> import z3c.form
  >>> context = xmlconfig.file('meta.zcml', z3c.form)
  >>> from z3c.form import testing
  >>> testing.setupFormDefaults()

We need a custom snippet template

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()
  >>> file = os.path.join(temp_dir, 'snippet_div_input.pt')
  >>> open(file, 'w').write('''
  ... <div tal:content="structure view/label">label</div>
  ... <div tal:content="structure view/render">widget</div>
  ... ''')

Now we register it

  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:z3c="http://namespaces.zope.org/z3c">
  ...   <z3c:snippetTemplate
  ...       name="div"
  ...       mode="input"
  ...       template="%s"
  ...       />
  ... </configure>
  ... """ % file, context=context)

And now we do that for a different snippet and register it under a
different name

  >>> file = os.path.join(temp_dir, 'snippet_span_input.pt')
  >>> open(file, 'w').write('''
  ... <div>
  ... <span tal:replace="structure view/label" />:
  ... <span tal:replace="structure view/render" />
  ... </div>
  ... ''')
  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:z3c="http://namespaces.zope.org/z3c">
  ...   <z3c:snippetTemplate
  ...       name="span"
  ...       mode="input"
  ...       template="%s"
  ...       />
  ... </configure>
  ... """ % file, context=context)

Now we need a template for our form, which demonstrates the use
of the different snippets.

  >>> file = os.path.join(temp_dir, 'myform.pt')
  >>> open(file, 'w').write('''
  ... <span tal:replace="structure view/widgets/myname/snippets/div" />
  ... <span tal:replace="structure view/widgets/myname/snippets/span" />
  ... ''')

We can see that the registered snippets are available under the widget
and the object "snippets".

We need some interface/class/browser view

  >>> class IPerson(zope.interface.Interface):
  ...    
  ...    myname=zope.schema.TextLine(title=u'Persons Name')
  >>> class Person(object):
  ...    zope.interface.implements(IPerson)
  ...    myname=''
  ...
  ...    def __init__(self, myname):
  ...       self.myname = myname

Now we create a form with our template, instantiate and update it 
(we use an AddForm as we have no context)

  >>> from z3c.form import form, field
  >>> from z3c.form.testing import TestRequest
  >>> from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
  >>> class PersonForm(form.AddForm):
  ...    
  ...    fields = field.Fields(IPerson)  
  ...    template = ViewPageTemplateFile('myform.pt', temp_dir)
  ...
  >>> request = TestRequest()
  >>> personForm = PersonForm(None, request)
  >>> personForm.update()

And now we render the form

  >>> print personForm.render()    
  <BLANKLINE>
  <BLANKLINE>
  <div>Persons Name</div>
  <div><input type="text" id="form-widgets-myname"
         name="form.widgets.myname"
         class="textWidget textline-field" value="" />
  </div>
  <BLANKLINE>
  <BLANKLINE>
  <div>
  Persons Name:
  <input type="text" id="form-widgets-myname"
         name="form.widgets.myname"
         class="textWidget textline-field" value="" />
  <BLANKLINE>
  </div>
  <BLANKLINE>
  <BLANKLINE>
