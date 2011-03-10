System Buildouts
****************

The system buildout script (``sbo``) provided by the zc.sbo package is
used to perform "system" buildouts that write to system directories
on unix-like systems.  They are run using ``sudo`` or as ``root`` so
they can write to system directiories.  You can install the ``sbo``
command into a Python environment using its setup script or a tool
like easy_install.

One installed, the ``sbo`` command is typically run with 2 arguments:

- The name of an application

- The name of a configuration

It expects the application to be a build-based application in
``/opt/APPLICATION-NAME``.  It expects to find a buildout
configuration in ``/etc/APPLICATION-NAME/CONFIG-NAME.cfg``

For example, if invoked with::

   sbo myapp abccorp

It will run::

   /opt/myapp/bin/buildout buildout:directory=/opt/myapp \
      -oUc /etc/myapp/sbccorp.cfg

Run with the -h option to get additional help.


Changes
*******

0.6.1 (2011-03-10)
==================

- Add missing --version option to report sbo's version.


0.6.0 (2010-11-05)
==================

- Add --installation to point to a specific software installation to use.

0.1.0 (yyyy-mm-dd)
==================

Initial release
