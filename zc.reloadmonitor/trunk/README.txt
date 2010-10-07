zc.reloadmonitor
****************

zc.reloadmonitor provides a plug-in for zc.monitor. It allows you to
cause already imported modules to be reloaded.

To use, just connect to the monitor port and give the command::

  reload my.module

To configure/enable from Python, use::

  import zc.reloadmodule
  zc.reloadmonitor.configure()

To configure from ZCML, use::

  <include package="zc.reloadmonitor" />

Changes
*******

0.2.0 (2010-10-07)
==================

- Make the reload monitor compatible with zope.interface 3.5.

0.1.0 (2010-09-03)
==================

Initial release
