=================
Langauge Switcher
=================

Let's show how ``z3c.language.switch`` works:

Imports and placeless setup:

  >>> import zope.component
  >>> from zope.app.testing import placelesssetup
  >>> from z3c.language.switch import II18nLanguageSwitch
  >>> from z3c.language.switch.testing import IContentObject
  >>> from z3c.language.switch.testing import II18nContentObject
  >>> from z3c.language.switch.testing import I18nContentObject
  >>> from z3c.language.switch.testing import I18nContentObjectLanguageSwitch
  >>> from z3c.language.switch.testing import ContentObject
  >>> placelesssetup.setUp()

Setup test object:

  >>> en_title = u'en_title'
  >>> obj = I18nContentObject(en_title)
  >>> obj.title
  u'en_title'

Add additional languages:

  >>> de_title = u'de_title'
  >>> fr_title = u'fr_title'
  >>> deObj = obj.addLanguage('de', de_title)
  >>> frObj = obj.addLanguage('fr', fr_title)

Switch default language:

  >>> obj.title
  u'en_title'

  >>> obj.setDefaultLanguage('de')
  >>> obj.title
  u'de_title'

Remove the 'en' language object:

  >>> obj._data.keys()
  ['de', 'en', 'fr']
  >>> obj.removeLanguage('en')
  >>> obj._data.keys()
  ['de', 'fr']

Remove default language object will end in a ``ValueError`` error:

  >>> obj.removeLanguage('de')
  Traceback (most recent call last):
  ...
  ValueError: cannot remove default language (de)

Remove nonexistent language object will end in a ``ValueError`` error:

  >>> obj.removeLanguage('undefined')
  Traceback (most recent call last):
  ...
  ValueError: cannot remove nonexistent language (undefined)

Set default language to a non existent language will end in a ``ValueError``:

  >>> obj.setDefaultLanguage('en')
  Traceback (most recent call last):
  ...
  ValueError: cannot set nonexistent language (en) as default

Access the language directly via the ``II18nLanguageSwitch`` adapter,
first register the adapter for the ``I18nContentObject``:

  >>> zope.component.provideAdapter(I18nContentObjectLanguageSwitch,
  ...     (II18nContentObject,), provides=II18nLanguageSwitch)

The adapter is set to the default language in the init method:

  >>> adapted = II18nLanguageSwitch(obj)
  >>> adapted.title
  u'de_title'

Change the default language and access the title again, the title should not
switch to another language:

  >>> obj.setDefaultLanguage('fr')
  >>> adapted.title
  u'de_title'

Switch the language to 'fr'  via the adapter:

  >>> adapted.setLanguage('fr')
  >>> adapted.title
  u'fr_title'

Finally, clean up:

  >>> placelesssetup.tearDown()


``AvailableLanguagesVocabulary`` Vocabulary
-------------------------------------------

Use this vocabulary for get the available languages from the object
itself.

  >>> from z3c.language.switch import vocabulary
  >>> vocab = vocabulary.AvailableLanguagesVocabulary(obj)
  >>> len(vocab._terms)
  2

  >>> vocab._terms[0].value
  'de'
  >>> vocab._terms[0].token
  'de'
  >>> vocab._terms[0].title
  'de'
  >>> vocab._terms[1].value
  'fr'
  >>> vocab._terms[1].token
  'fr'
  >>> vocab._terms[1].title
  'fr'
