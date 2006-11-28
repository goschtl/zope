This is:

* an experimental integration of Zope 3 with the CherryPy WSGI server.

* an attempt to see how much of Zope needs to be loaded in order to
  run Grok.

These two aims are combined as running Zope 3 in a completely different
server context makes it very easy to test a barebones Zope 3 installation
at the same time.

The experiment is far from finished yet: I've barely scratched the
surface of testing Grok, and I hope that we can get away with loading
less of Zope 3 on startup, as I'd like to speed up startup/shutdown further.

