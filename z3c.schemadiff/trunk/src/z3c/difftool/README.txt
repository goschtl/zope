z3c.schemadiff
============

Let's set up a schema describing objects we want to diff.

  >>> class IPizza(interface.Interface):
  ...     name = schema.TextLine(title=u"Name")
  ...     toppings = schema.Set(
  ...        title=u"Toppings",
  ...        value_type=schema.TextLine(),
  ...     )

A class definition.

  >>> class Pizza(object):
  ...     interface.implements(IPizza)
  ...
  ...     def __init__(self, name, toppings):
  ...         self.name = name
  ...         self.toppings = toppings
  
Add two instances, a classic Margherita and a Roman Capricciosa pizza.

  >>> margherita = Pizza(u"Margherita",
  ...    (u"Tomato", u"Mozzarella", u"Basil"))
  
  >>> capricciosa = Pizza(u"Capricciosa",
  ...    (u"Tomato", u"Mozarella", u"Mushrooms", u"Artichokes", u"Prosciutto"))

To compare these, we need to register a field diff component for each
of our fields.

  >>> from z3c.schemadiff import field

  >>> component.provideAdapter(field.TextLineDiff)
  >>> component.provideAdapter(field.SetDiff)
  
Let's try it out.

  >>> from z3c.schemadiff.interfaces import IFieldDiff

  >>> name = IFieldDiff(IPizza['name'])
  >>> name.lines(margherita.name)
  (u'Margherita',)

  >>> toppings = IFieldDiff(IPizza['toppings'])
  >>> toppings.lines(margherita.toppings)
  (u'Tomato', u'Mozzarella', u'Basil')
  
Now we can make a diff of the two instances.

  >>> from z3c.schemadiff import schema
  >>> schema.diff(margherita, capricciosa)
  {<zope.schema._field.Set object at ...>:
        ((u'Tomato', u'Mozzarella', u'Basil'),
         (u'Tomato', u'Mozarella', u'Mushrooms', u'Artichokes', u'Prosciutto')),
   <zope.schema._bootstrapfields.TextLine object at ...>:
        ((u'Margherita',),
         (u'Capricciosa',))}
