======================
 Autocomplete Widgets
======================

Autocomplete widgets are an alternative to normal select widgets.

  >>> from z3c.widget.autocomplete.widget import AutoCompleteWidget

Let us create a vocabulary.

  >>> from zope.schema.vocabulary import SimpleVocabulary
  >>> from zope.publisher.browser import TestRequest
  >>> from zope import schema, component, interface
  >>> items = ((u'value1',1,u'Title1'),
  ...          (u'value2',2,u'Title2'),
  ...          (u'value3',3,u'Title3'))
  >>> terms = map(lambda i: SimpleVocabulary.createTerm(*i),items)
  >>> voc = SimpleVocabulary(terms)
  >>> [term.title for term in voc]
  [u'Title1', u'Title2', u'Title3']
  >>> field = schema.Choice(__name__='foo',
  ...     missing_value=None,
  ...     vocabulary=voc)
  >>> request = TestRequest()
   >>> widget =  AutoCompleteWidget(field, request)
  >>> widget
  <z3c.widget.autocomplete.widget.AutoCompleteWidget object at ...>
  >>> print widget()
  <input class="textType" id="field.foo" name="field.foo" type="text" value=""  />
  <div id="field.foo.target" class="autoComplete"></div>
  <script type="text/javascript">
  new Ajax.Autocompleter('field.foo','field.foo.target',
  'http://127.0.0.1/++widget++field.foo/suggestions'
  ,options={
  paramName: 'value'
  });
  </script>

Let's add some input. Note that the input must match the title of the
vocabulary term.

  >>> request.form['field.foo']=u'Title1'
  >>> widget.getInputValue()
  u'value1'

If we have no matching title a ConversionError is raised.

  >>> request.form['field.foo']=u'Unknown'
  >>> widget.getInputValue()
  Traceback (most recent call last):
  ...
  ConversionError: ('Invalid value', u'Unknown')

Also the form value is the title of the term with the given value.

  >>> widget._toFormValue('value1')
  u'Title1'

  >>> suggestions = widget.getSuggestions('Title')
  >>> [title for title in suggestions]
  [u'Title1', u'Title2', u'Title3']
  >>> suggestions = widget.getSuggestions('Title1')
  >>> [title for title in suggestions]
  [u'Title1']
  >>> suggestions = widget.getSuggestions('ABC')
  >>> [title for title in suggestions]
  []
  >>> suggestions = widget.getSuggestions('title')
  >>> [title for title in suggestions]
  [u'Title1', u'Title2', u'Title3']
