=====================
megrok.z3cform.layout
=====================

`megrok.z3cform.layout` provides several useful templates that can be
used out-of-the-box with `megrok.z3cform.base`. These templates are
totally independent from the megrok.z3cform.base library, meaning you
can simply swap or override them.

`megrok.z3cform.layout` also provides some common handlers to enhance
a basic form such as a Cancel Button.


Setup
-----

Let's start with a simple example. We create a person object:

   >>> from zope.interface import Interface, implements
   >>> from zope.schema import TextLine

The Interface of our Object:

   >>> class IPerson(Interface):
   ...     name = TextLine(title = u'Name')
   ...     age = TextLine(title = u'Age')

The class of our Object:

   >>> class Person(object):
   ...     implements(IPerson)
   ...     name = u""
   ...     age = u""

And our instance:

   >>> peter = Person()
   >>> peter
   <megrok.z3cform.base.ftests.Person object at ...>

   >>> IPerson.providedBy(peter)
   True


Creating some Forms for it
--------------------------

   >>> from megrok.z3cform.base import EditForm, Fields
   >>> from grokcore.component import context, implements
   >>> from grokcore.component.testing import grok, grok_component

To include a cancel Button in your Form, it simply needs to declare it
using the directive

   >>> from megrok.z3cform.layout import cancellable

   >>> class Add(EditForm):
   ...     cancellable(True)
   ...     context(Interface)
   ...     fields = Fields(IPerson)

   >>> grok_component('add', Add)
   True

   >>> from zope.component import getMultiAdapter
   >>> from zope.publisher.browser import TestRequest
   >>> request = TestRequest()

   >>> add = getMultiAdapter((peter, request), name="add")
   >>> print add()
   <form action="http://127.0.0.1" method="post"
         enctype="multipart/form-data" class="form-add">
     <div class="errors">
     </div>
     <p class="documentDescription"></p>
     <input type="hidden" name="camefrom" />
       <div id="edition-fields">
       <div class="field ">
         <label for="form-widgets-name">
           <span>Name</span>
           <span class="fieldRequired" title="Required">
             <span class="textual-info">(Required)</span>
           </span>
         </label>
         <div class="widget">
       <input id="form-widgets-name" name="form.widgets.name"
              class="text-widget required textline-field"
              value="" type="text" />
   </div>
       </div>
       <div class="field ">
         <label for="form-widgets-age">
           <span>Age</span>
           <span class="fieldRequired" title="Required">
             <span class="textual-info">(Required)</span>
           </span>
         </label>
         <div class="widget">
       <input id="form-widgets-age" name="form.widgets.age"
              class="text-widget required textline-field"
              value="" type="text" />
   </div>
       </div>
       </div>
       <div id="actionsView">
         <span class="actionButtons">
   <input id="form-buttons-apply" name="form.buttons.apply"
          class="submit-widget button-field" value="Apply"
          type="submit" />
   <input id="form-buttons-cancel" name="form.buttons.cancel"
          class="submit-widget cancelbutton-field"
          value="Cancel" accesskey="c" type="submit" />
         </span>
       </div>
   </form>


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
