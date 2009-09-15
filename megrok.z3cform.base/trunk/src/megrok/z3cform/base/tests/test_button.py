"""
As it's a martian directive, it's inherited :

   >>> class AnotherForm(Add):
   ...     context(Interface)
   ...     fields = Fields(IPerson)

   >>> grok_component('anotherform', AnotherForm)
   True

   >>> anotherform = getMultiAdapter((peter, request), name="anotherform")
   >>> "form.buttons.cancel" in anotherform()
   True


If you need to explicitly remove the use of a Cancel button from a
form, you can remove it by declaring the cancellable directive set to False:

   >>> class YetAnotherForm(Add):
   ...     context(Interface)
   ... 	   cancellable(False)
   ...     fields = Fields(IPerson)

   >>> grok_component('yetanotherform', YetAnotherForm)
   True

   >>> yetanotherform = getMultiAdapter((peter, request),
   ...                                  name="yetanotherform")
   >>> "form.buttons.cancel" in yetanotherform()
   False
"""
