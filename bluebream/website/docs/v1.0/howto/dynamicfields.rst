Dynamic fields in forms
=======================

.. based on: http://wiki.zope.org/zope3/HowDoIUseDynamicFieldsInFormlib

To add fields dynamically using ``zope.formlib`` machinery, one
should avoid subclassing ``form.EditForm``.  The ``form.EditForm``
would require you to also setup an adapter for your form field.  The
following code shows what is involved in having a custom field inside
your form.

::

  from zope.formlib import form
  from zope.schema import TextLine
  
  class TestForm(form.PageForm):
         my_field_name = 'something'
 
     def __init__(self, context, request):
         super(TestForm, self).__init__(context, request)
         self.form_fields = form.Fields(TextLine(__name__=self.my_field_name,
                                                 title=u"Test Field")) 
 
     def setUpWidgets(self, ignore_request=False):
         name = self.name
         self.widgets = form.setUpWidgets(
                           self.form_fields, self.prefix, self.context, self.request, 
                           data={self.my_field_name:SOME_VALUE}, 
                           ignore_request=ignore_request)
 
     @form.action(label=_("Submit"))
     def handleSubmitAction(self, action, data):
         #do something relevant to you here

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
