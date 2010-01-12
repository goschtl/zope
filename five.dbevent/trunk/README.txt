five.dbevent
============

Backport the notification of ``DatabaseOpenedWithRoot`` event to Zope 2.

This might be useful to initialize components once the zope database is ready (see also ``zope.app.generations``)

Install
-------

As its setup is done with ``collective.monkeypatcher``, you need to include ``five.dbevent`` configure.zcml

Implementation
--------------

The package adds an ``__init__`` method to ``Zope2.App.startup.TransactionsManager``. It sends the ``DatabaseOpenedWithRoot`` event when
the ``TransactionsManager`` is instantiated. This happens just after the initialization of the root folder (see ``Zope2.App.startup.startup``).
