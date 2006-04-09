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

    >>> from multiform.multiform import MultiFormBase,ItemFormBase
    >>> from zope.formlib import form

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
    <div>0</div><div><input ... name="form.0.name" ... value="n0" ...</div>
    </div>
    <div>
    ...
    </div>

If the request contains any form data, that will be reflected in the
output:

    >>> request.form['form.1.name'] = u'bob'
    >>> print OrdersForm(orderMapping,request)()
    <div>
    ...
    <div>1</div><div><input ... name="form.1.name" ... value="bob" ...</div>
    ...
    </div>

Sometimes we don't want this behavior: we want to ignore the request values,
particularly after a form has been processed and before it is drawn again.
This can be accomplished with the 'ignore_request' argument in
setUpWidgets.

    >>> print OrdersForm(orderMapping, request)(ignore_request=True)
    <div>
    ...
    <div>1</div><div><input ... name="form.1.name" ... value="n1" ...</div>
    ...
    </div>

In order to define a save action on the multiform we have to define a
parent action on our OrderForm. A parent action is rendered only one
time in the parent multiform, but applied to all subforms.

    >>> from multiform import multiform
    >>> class OrderForm2(ItemFormBase):
    ...     form_fields = form.Fields(IOrder,omit_readonly=False,
    ...     render_context=True)
    ...     def update(self):
    ...         super(OrderForm2,self).update()
    ...         
    ...     @multiform.parentAction(u"Save")
    ...     def handle_save_action(self, action, data):
    ...         form.applyChanges(self.context, self.form_fields,
    ...         data, self.adapters)
    ...     def render(self):
    ...         return '\n<div>%s</div>\n' % '</div><div>'.join([w() for w in
    ...     self.widgets])


Now we have to set the factory on the OrdersForm.

    >>> class OrdersForm2(OrdersForm):
    ...     itemFormFactory=OrderForm2
    ...     def __call__(self, ignore_request=False):
    ...         self.setUpWidgets()
    ...         res = u''
    ...         names = sorted(self.subForms.keys())
    ...         for name in names:
    ...             res += '<div>%s</div>\n' % self.subForms[name]()
    ...         return res



    >>> pf = OrdersForm2(orderMapping,request)
    >>> pf.setUpWidgets()
    >>> action = [action for action in pf.subForms['1'].actions][0]
    >>> action
    <multiform.multiform.ParentAction object at ...>

The name of the action is without the item key, because it is applied
 to all items.

    >>> print action.__name__
    actions.save

    >>> request = TestRequest()
    >>> orderMapping = dict([(str(k),Order(k,name='n%s'%k)) for k in range(2)])
    >>> request.form[pf.prefix + '.' + action.__name__]=u''
    >>> print OrdersForm2(orderMapping,request)()
    Traceback (most recent call last):
    ...
    FormError: ('No input', 'name')

Ups, we have an error because we didn't provide the input data on the
request. The form requires to have all input fields in the request if
an action should be supplied.

Let's supply request Data.

    >>> for i in range(2):
    ...     request.form['form.%s.name' % i]='new name %s' % i
    ...     request.form['form.%s.identifier' % i]= i
    >>> print OrdersForm2(orderMapping,request)()
    <div>
    <div... value="new name 0" ...
    <div... value="new name 1" ...
    </div>



TODO:

- encode prefix, do we have to do it?

