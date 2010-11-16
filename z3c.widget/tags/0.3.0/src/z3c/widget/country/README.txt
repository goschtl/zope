=========================
Country selection Widgets
=========================

This package provides widgets to select a country.
The dropdown type is registered as a default for the Country schema.

The pain was to sort the options after the translation.



Before we can start, we have to do a little bit of setup:

  >>> import zope.component
  >>> import zope.schema
  >>> import zope.app.form.browser
  >>> from z3c.widget.country.widget import CountryInputDropdown
  >>> from z3c.widget.country import ICountry
  >>> from z3c.i18n.iso import territoryVocabularyFactory
  >>> from zope.publisher.interfaces.browser import IBrowserRequest

First we have to create a field and a request:

  >>> from z3c.widget.country import Country

  >>> countryFld = Country(
  ...     __name__='country',
  ...     title=u'Country',
  ...     description=u'Select a Country')

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

Now we can initialize the widget.

  >>> class Content(object):
  ...     country = None
  >>> content = Content()
  >>> boundCountry = countryFld.bind(content)

  >>> widget = CountryInputDropdown(boundCountry,
  ...   territoryVocabularyFactory(None), request)

Let's make sure that all fields have the correct value:

  >>> widget.name
  'field.country'

  >>> widget.label
  u'Country'

  >>> widget.hint
  u'Select a Country'

  >>> widget.visible
  True

Let's see how the widget is rendered:

  >>> print widget()
  <div>
  <div class="value">
  <select id="field.country" name="field.country" size="1" >
  <option value="AF">Afghanistan</option>
  <option value="AL">Albania</option>
  <option value="DZ">Algeria</option>
  ...
  <option value="HU">Hungary</option>
  <option value="IS">Iceland</option>
  <option value="IN">India</option>
  ...
  <option value="ZM">Zambia</option>
  <option value="ZW">Zimbabwe</option>
  </select>
  ...

#Let's see the german translation:
#z3c.i18n registrations required!!!
#
#  >>> request = TestRequest(HTTP_ACCEPT_LANGUAGE='de')
#
#  >>> widget = CountryInputDropdown(boundCountry,
#  ...   territoryVocabularyFactory(None), request)
#
#  >>> print widget()
#  <div>
#  <div class="value">
#  <select id="field.country" name="field.country" size="1" >
#  <option value="AF">Afghanistan</option>
#  <option value="AL">Albania</option>
#  <option value="DZ">Algeria</option>
#  ...
#  <option value="HU">Hungary</option>
#  <option value="IS">Iceland</option>
#  <option value="IN">India</option>
#  ...
#  <option value="ZM">Zambia</option>
#  <option value="ZW">Zimbabwe</option>
#  </select>
#  ...
