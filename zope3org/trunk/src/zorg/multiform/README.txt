===================
 Multiform Package
===================

This Package provides an API to handle multiple forms with matching
form fields on multiple items. The cration of multiforms is derived
from the Form class of the formlib package.

    >>> from zope import interface, schema
    >>> class IOrder(interface.Interface):
    ...     identifier = schema.Int(title=u"Identifier", readonly=True)
    ...     name = schema.TextLine(title=u"Name")
    >>> class Order:
    ...     interface.implements(IOrder)
    ...
    ...     def __init__(self, identifier, name=''):
    ...         self.identifier = identifier
    ...         self.name = name

    >>> orderMapping = dict([(str(k),Order(k,name='n%s'%k)) for k in range(5)])


Let us create a new multiform class which should display IOrder objects.

    >>> from multiform.multiform import MultiForm,ItemFormBase
    >>> from zope.formlib import form

    >>> class OrderForm(ItemFormBase):
    ...     def __call__(self, ignore_request=False):
    ...         widgets = form.setUpWidgets(
    ...             self.form_fields, self.prefix, self.context, self.request,
    ...             ignore_request=ignore_request)
    ...         return '\n<div>%s</div>\n' % '</div><div>'.join([w() for w in
    ...     widgets])


    >>> class OrdersForm(MultiForm):
    ...     
    ...     form_fields = form.Fields(IOrder)
    ...     
    ...     def __call__(self, ignore_request=False):
    ...         self.setUpForms()
    ...         res = u''
    ...         for form in self.forms.values():
    ...             res += '<div>%s</div>\n' % form(ignore_request=True)
    ...         return res
    ...     
    ...     def itemForm(self, item, **kwargs):
    ...         return OrderForm(item, self, **kwargs)



    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> view = OrdersForm(orderMapping, request)
    >>> print view()
    <div>
    <div>1</div><div>n1</div>
    </div>
    <div>
    ...
    <div>
    <div>4</div><div>n4</div>
    </div>



TODO:

- encode prefix, do we have to do it?

