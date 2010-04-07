Introduction
============

``zope.z2releases`` is used to generated a PyPI compatible index with
references to all pinned package versions based on the ``versions.cfg``
configuration of the Zope 2 package.

Usage
=====

To generate an index, use::

    z2_kgs tags/2.12.1 /srv/index/2.12.1
    z2_kgs branches/2.12 /srv/index/2.12
