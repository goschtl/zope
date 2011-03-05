.. module:: zope.pytest

`zope.pytest` API
*****************

Helpers for py.test integration in Zope-based environments.

The main test helpers are the first two functions (:func:`create_app`,
:func:`configure`) which are normally accessed deploying the py.test_
`funcarg`_ mechanism.


:func:`create_app`
==================

.. autofunction:: zope.pytest.create_app

:func:`configure`
=================

.. autofunction:: zope.pytest.configure

:func:`setup_config`
====================

.. autofunction:: zope.pytest.setup_config

:func:`teardown_config`
=======================

.. autofunction:: zope.pytest.teardown_config


:func:`setup_db`
================

.. autofunction:: zope.pytest.setup_db

:func:`teardown_db`
===================

.. autofunction:: zope.pytest.teardown_db

:func:`setup_connection`
========================

.. autofunction:: zope.pytest.setup_connection

:func:`teardown_connection`
===========================

.. autofunction:: zope.pytest.teardown_connection

:func:`setup_root`
==================

.. autofunction:: zope.pytest.setup_root

:func:`teardown_root`
=====================

.. autofunction:: zope.pytest.teardown_root


.. _py.test: http://pytest.org/

.. _funcarg: http://pytest.org/funcargs.html

.. _ZODB: http://www.zodb.org/

.. _ZCML: http://www.muthukadan.net/docs/zca.html#zcml
