=====================
megrok.z3cform.layout
=====================

`megrok.z3cform.layout` provides generic templates that can be used
out-of-the-box with `megrok.z3cform.base`. These templates are totally
independent from the megrok.z3cform.base library, meaning you can
simply swap or override them.

Getting started
===============

We import the base components to test our form layout::

   >>> from megrok.z3cform.base import DisplayForm, EditForm, Fields
   >>> from grokcore.component import context, implements
   >>> from grokcore.component.testing import grok, grok_component

Let's start with a simple example. We create a person object:

   >>> from zope.interface import Interface, implements
   >>> from zope.schema import TextLine

The Interface of our Object:

   >>> class IPerson(Interface):
   ...   name = TextLine(title = u'Name')
   ...   age = TextLine(title = u'Age')

The class of our Object:

   >>> class Person(object):
   ...   implements(IPerson)
   ...   name = u""
   ...   age = u""

And our instance:

   >>> peter = Person()
   >>> peter
   <megrok.z3cform.base.ftests.Person object at ...>

   >>> IPerson.providedBy(peter)
   True


Rendering forms
===============

For now, megrok.z3cform.layout provides only one template that works
for all the different kinds of forms::

   >>> class Edit(EditForm):
   ...   context(Interface)
   ...   fields = Fields(IPerson)

   >>> grok_component('edit', Edit)
   True

   >>> from zope.component import getMultiAdapter
   >>> from zope.publisher.browser import TestRequest
   >>> request = TestRequest()

   >>> edit = getMultiAdapter((peter, request), name="edit")
   >>> print edit()
   <form action="http://127.0.0.1" method="post"
         enctype="multipart/form-data" class="form-edit">
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
         </span>
       </div>
   </form>

It works the same for a form with no actions::

   >>> class Display(DisplayForm):
   ...   context(Interface)
   ...   fields = Fields(IPerson)

   >>> grok_component('display', Display)
   True

   >>> view = getMultiAdapter((peter, request), name="display")
   >>> print view()
   <form action="http://127.0.0.1" method="post"
         enctype="multipart/form-data" class="form-display">
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
              <span id="form-widgets-name"
                    class="text-widget required textline-field"></span>
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
             <span id="form-widgets-age"
                   class="text-widget required textline-field"></span>
           </div>
    	 </div>
       </div>
    </form>
