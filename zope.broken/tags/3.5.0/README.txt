==================
zope.broken README
==================

This package defines a marker interface, ``zope.broken.IBroken``, used
to identify objects which cannot be correctly loaded from the ZODB,
typically because the class named in their pickle is not importable.

The package exists as a dependency inversion, preventing packages which
need to use this interface (e.g., ``zope.container``) from inheriting
the dependencies of ``zope.app.broken`` (where the interface used to be
defined).
