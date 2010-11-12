================
zc.signalhandler
================

This package allows registration of signal handlers from ``ZConfig``
configuration files within the framework provided by the Zope Toolkit.

Any number of handlers may be registered for any given signal.

To use this from your ``zope.conf`` file, ensure this package is
available to your application, and include a section like this::

    %import zc.signalhandler

    <signalhandlers log-handling>
       USR1  ZConfig.components.logger.loghandler.reopenFiles
       USR1  yourapp.tasks.doSomethingUseful
    </signalhandlers>

See the ``README.txt`` inside the ``zc.signalhandler`` package for
complete documentation.


Release history
===============

1.2 (2010-11-12)
----------------

- Moved development to zope.org, licensed under the ZPL 2.1.


1.1 (2007-06-21)
----------------

This was a Zope Corporation internal release.

- Fix compatibility with ``zope.app.appsetup.product``.


1.0 (2007-06-21)
----------------

Initial Zope Corporation internal release.
