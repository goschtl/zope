*****************************************
ZC Buildout recipe for Redhat RC scripts
*****************************************

This package provides a zc.buildout recipe for creating Red-Hat Linux
compatible run-control scripts.

.. contents::

Changes
*******

1.1.0 (2008/02/01)
==================

Use the deployment name option (as provided by zc.recipe.deployment
0.6.0 and later) if present when generating script names.

Use the deployment rc-directory as the destination when a deployment
is used.

Use /sbin/chkconfig rather than chkconfig, as I'm told it is always in
that location and rarely in anyone's path. :)

1.0.0 (2008/01/15)
==================

Initial public release
