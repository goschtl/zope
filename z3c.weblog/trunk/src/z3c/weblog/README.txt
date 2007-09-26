=============================
A Basic Weblog Implementation
=============================


z3c.weblog is a simple weblog implementation using BTreeContainers

    >>> from zope.interface.verify import verifyClass
    >>> from z3c.weblog.weblog import Weblog
    >>> from z3c.weblog.interfaces import IWeblog
    >>> verifyClass(IWeblog, Weblog)
    True

Let's make sure we can intantiate the weblog:

    >>> weblog = Weblog()
    >>> weblog
    <z3c.weblog.weblog.Weblog object at ...>

