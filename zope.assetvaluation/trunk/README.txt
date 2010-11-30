Methodology for ``zope.assetvaluation``
=======================================


This package provides a ``zope-org-valuation`` script that is run
against the zope.org Subversion repository. The script checks out the
``trunk`` or ```develop`` branches  of all top level subversion projects,
with the exception of ``Sandbox``.  For each project, the script runs the
``sloccount`` script[1] against its checkout, and aggregates the total
lines of code / valuation, based on the "Organic" COCOMO model[1].


[1] http://www.dwheeler.com/sloccount/sloccount.html

[2] http://www.dwheeler.com/sloccount/sloccount.html#cocomo
