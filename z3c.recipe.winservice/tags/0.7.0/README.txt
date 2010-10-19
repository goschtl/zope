=====================
z3c.recipe.winservice
=====================

This recipe offers windows service installation support.

The 'service' recipe installes the required scripts and files which can be
used to install a windows service.

Using the ``runscript`` option it is able to make any executable a service.


Options
*******

The 'service' recipe accepts the following options:

name
  The windows service name option.

description
  The windows service description option.

runzope
  The script name which gets run by the winservice.
  If the script name contains any path, it's taken as it is, otherwise the
  buildout bin folder is prepended. winservice will check on install if this
  script exists.
  The install takes care of adding ``-script.py`` if necessary.
  This script can get setup for exmaple with the z3c.recipe.dev.app recipe.

runscript
  The script (.py) or executable (.exe) name to be run by the winservice.
  The value will get NO treatment, you need to pass an exact specification.
  winservice will check on install if this script/exe exists.
  Use this option OR runzope, but never both.

parameters
  This value will get passed to the script (runzope or runscript) as a
  parameter. The value will get NO treatment, you need to take care of adding
  any quotes if necessary.

debug
  Adding this option to the recipe wraps the whole script to run into
  a catch all except that logs the exception to the windows event log.
  This is good for debugging weird exceptions that occur before the Zope
  logging system is in place.
  This does not work if runscript is an executable.

