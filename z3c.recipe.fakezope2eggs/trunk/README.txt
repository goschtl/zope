Fake Zope 2 Eggs
================

Zope 2 isn't eggified yet, Zope 3 does. That can become a problem if you want to
install some egg with depedencies related to Zope 3 eggs (such as zope.interface,
zope.component, ...)

This buildout recipe will simply add some fake egg link to zope libraries (installed
inside zope/lib/python/zope/...) so that setuptools can see that the dependencies are
already satisfied and it won't fetch them anymore.


