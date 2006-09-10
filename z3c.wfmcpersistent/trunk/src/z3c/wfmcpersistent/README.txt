=============================================
Workflow-Management Coalition Workflow Engine
=============================================

This package has exactly the same functionality as the zope.wfmc,
but all classes are redefined as persistent to be able to store
the complete workflow process definition in the ZODB.

Differences
===========

Class names are not changed to make switching to the persistent version easy.

A utility is added to work as a workflow process definition registry.

Requirements
============

:zope.wfmc: at the moment comes with the Zope 3 release

See: http://svn.zope.org/Zope3/trunk/src/zope/wfmc/

Installation
============

Drop the `z3c.wfmcpersistent` folder somewhere on the PYTHONPATH.
Copy the `wfmcpersistent-configure.zcml` to your instace's etc folder.

TODO
====
see todo.txt
