===================
 Multiform Package
===================

This Package provides an API to handle multiple forms with matching
form fields on multiple items. The creation of multiforms is derived
from the Form class of the formlib package.

    >>> from zope import interface, schema
    >>> from zope.location.interfaces import ILocation

    >>> class IOrder(interface.Interface):
    ...     identifier = schema.Int(title=u"Identifier", readonly=True)
    ...     name = schema.TextLine(title=u"Name")
    >>> class Order(object):
    ...     interface.implements(IOrder,ILocation)
    ...
    ...     def __init__(self, identifier, name=''):
    ...         self.identifier = identifier
    ...         self.name = name
    ...         self.__name__ = name

    >>> orderMapping = dict([(str(k),Order(k,name='n%s'%k)) for k in range(5)])

Let us create a new multiform class which should display IOrder objects.

    >>> from zope.formlib import form
    >>> from z3c.multiform.multiform import MultiFormBase,ItemFormBase

    >>> class OrderForm(ItemFormBase):
    ...     form_fields = form.Fields(IOrder,omit_readonly=False,
    ...     render_context=True)
    ...     def __call__(self, ignore_request=False):
    ...         widgets = form.setUpWidgets(
    ...             self.form_fields, self.prefix, self.context, self.request,
    ...             ignore_request=ignore_request)
    ...         return '\n<div>%s</div>\n' % '</div><div>'.join([w() for w in
    ...     widgets])


    >>> class OrdersForm(MultiFormBase):
    ...     
    ...     itemFormFactory = OrderForm
    ...     def __call__(self, ignore_request=False):
    ...         self.setUpWidgets()
    ...         res = u''
    ...         names = sorted(self.subForms.keys())
    ...         for name in names:
    ...             res += '<div>%s</div>\n' % self.subForms[name](
    ...             ignore_request=ignore_request)
    ...         return res
    ...
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> view = OrdersForm(orderMapping, request)
    >>> print view()
    <div>
    <div>0</div><div><input ... name="form.sf.0.name" ... value="n0" ...</div>
    </div>
    <div>
    ...
    </div>

If the request contains any form data, that will be reflected in the
output:

    >>> request.form['form.sf.1.name'] = u'bob'
    >>> print OrdersForm(orderMapping,request)()
    <div>
    ...
    <div>1</div><div><input ... name="form.sf.1.name" ... value="bob" ...</div>
    ...
    </div>

Sometimes we don't want this behavior: we want to ignore the request values,
particularly after a form has been processed and before it is drawn again.
This can be accomplished with the 'ignore_request' argument in
setUpWidgets.

    >>> print OrdersForm(orderMapping, request)(ignore_request=True)
    <div>
    ...
    <div>1</div><div><input ... name="form.sf.1.name" ... value="n1" ...</div>
    ...
    </div>

