======
README
======

The package provides a simple access to a session for store a language.

  >>> from zope.session.interfaces import ISession
  >>> from zope.session.session import PersistentSessionDataContainer
  >>> from zope.session import tests
  >>> from z3c.language.session import interfaces
  >>> from z3c.language.session import app

We have to setup a session data container and create a test request:

  >>> request = tests.setUp(PersistentSessionDataContainer)

We can simply create a session with the request as attribute:

  >>> langSession = app.LanguageSession(request)

Such a session provides ILanguageSession:

  >>> interfaces.ILanguageSession.providedBy(langSession)
  True

And the base ISession interface:

  >>> ISession.providedBy(langSession)
  True


getLanguage
-----------

We can check if there is a language set in the session with getLanguage. If no
language is set, it should be None:

  >>> langSession.getLanguage()


setLanguage
-----------

The session provides setLanguage which can set a language:

  >>> langSession.setLanguage('de')

Now we should get the new language stored in the session:

  >>> langSession.getLanguage()
  'de'
