==========
Negotiator
==========

This package provides a local implementation of the ``INegotiator`` interface
defined in ``zope.i18n.interfaces``. The negotiator implementation offers some
additional usefull attributes which are explained later. This ``INegotiator``
is also used in the ``z3c.language.switch`` package.

Let's setup a negotiator:

  >>> from z3c.language.negotiator import app
  >>> negotiator = app.Negotiator()

Such a negotiator provides the following interfaces:

  >>> from zope.i18n.interfaces import INegotiator
  >>> from z3c.language.negotiator.interfaces import INegotiatorManager

  >>> INegotiator.providedBy(negotiator)
  True
  >>>
  >>> INegotiatorManager.providedBy(negotiator)
  True
  >>>

By default a negotiator has the following values:

  >>> negotiator.policy
  'session --> browser --> server'

  >>> negotiator.serverLanguage
  u'en'

  >>> negotiator.offeredLanguages
  []

If we set a policy with a wrong value, we will get a ValueError:

  >>> negotiator.policy = u'wrong'
  Traceback (most recent call last):
  ...
  ValueError: ('Not a valid policy name.', u'wrong')

Let's add the negotiator to the site root:

  >>> rootFolder['negotiator'] = negotiator

And register the negotiator as a utility:

  >>> import zope.component
  >>> sitemanager = zope.component.getSiteManager(rootFolder)
  >>> sitemanager.registerUtility(negotiator, INegotiator)

After register the negotiator as a utility, we can use the vocabulary and see
what offered languages are available:

  >>> from z3c.language.negotiator import vocabulary
  >>> vocab = vocabulary.OfferedLanguagesVocabulary(None)
  >>> vocab
  <z3c.language.negotiator.vocabulary.OfferedLanguagesVocabulary object at ...>

  >>> vocab._terms
  []

Add some offered languages and check the vocabulary again:

  >>> negotiator.offeredLanguages = [u'de', u'fr']
  >>> negotiator.offeredLanguages
  [u'de', u'fr']

Try to get the utility and ceck the offeredLanguages again:

  >>> util = zope.component.getUtility(INegotiator)
  >>> util.offeredLanguages
  [u'de', u'fr']

Now check the vocabulary again:

  >>> vocab = vocabulary.OfferedLanguagesVocabulary(None)
  >>> vocab._terms[0].value
  u'de'
  >>> vocab._terms[0].token
  'de'
  >>> vocab._terms[0].title
  u'de'
  >>> vocab._terms[1].value
  u'fr'
  >>> vocab._terms[1].token
  'fr'
  >>> vocab._terms[1].title
  u'fr'

See ``tests.py`` for more tests.
