System Buildouts
****************

The system buildout script (``sbo``) provided by the zc.sbo package is
used to perform "system" buildouts that write to system directories
on unix-like systems.  They are run using ``sudo`` or as ``root`` so
they can write to system directiories.  You can install the ``sbo``
command into a Python environment using its setupo script or a tool
like easy_install.

One installed, the ``sbo`` command is typically run with 2 arguments:


Changes
*******

0.6.1 (unreleased)
==================

- Add missing --version option to report sbo's version.


0.6.0 (2010-11-05)
==================

- Add --installation to point to a specific software installation to use.

0.1.0 (yyyy-mm-dd)
==================

Initial release
