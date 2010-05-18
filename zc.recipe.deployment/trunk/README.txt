***********************
Unix Deployment Support
***********************

.. contents::

The zc.recipe.deployment recipe provides support for deploying
applications with multiple processes on Unix systems. (Perhaps support
for other systems will be added later.) It creates directories to hold
application instance configuration, log and run-time files.  It also
sets or reads options that can be read by other programs to find out
where to place files:

crontab-directory
    The name of the directory in which cron jobs should be placed.
    This is /etc/cron.d.

etc-directory
    The name of the directory where configuration files should be
    placed.  This is /etc/NAME, where NAME is the deployment
    name.

log-directory
    The name of the directory where application instances should write
    their log files.  This is /var/log/NAME, where NAME is
    the deployment name.

logrotate-directory
    The name of the directory where logrotate configuration files
    should be placed, typically, /etc/logrotate.d.

run-directory
    The name of the directory where application instances should put
    their run-time files such as pid files and inter-process
    communication socket files.  This is /var/run/NAME, where
    NAME is the deployment name.

rc-directory
    The name of the directory where run-control scripts should be
    installed.  This is /etc/init.d.

The etc, log, and run directories are created in such a way that the
directories are owned by the user specified in the user option and are
writable by the user and the user's group.

Changes
*******

0.8.0 (2010-05-18)
==================

Features Added
--------------

Added recipe for updating configuration files that may shared by
multiple applications.

0.7.1 (2010-03-05)
==================

Bugs fixed
----------

- Fixed a serious bug that cause buildouts to fail when using new
  versions of the deployment recipe with older buildouts.

- Made uninstall more tolerant of directories it's about to delete
  already being deleted.

0.7.0 (2010-02-01)
==================

Features Added
--------------

You can now specify a user for crontab entries that is different than
a deployment user.

0.6 (2008-02-01)
================

Features Added
--------------

Added the ability to specify a name independent of the section name.
Also, provide a name option for use by recipes.

Important note to recipe authors: Recipes should use the deployment
name option rather than the deployment name when computing names of
generated files.

0.5 (Mar 23, 2007)
==================

Features Added
--------------

Added recipe for generating crontab files in /etc/cron.d.

0.4 (Mar 22, 2007)
==================

Features Added
--------------

- Added setting for the logrotate configuration directories.

Bugs Fixed
----------

- The documentation gave the wrong name for the crontab-directory option.

0.3 (Feb 14, 2007)
==================

Features Added
--------------

- Added a configuration recipe for creating configuration files.

0.2.1 (Feb 13, 2007)
====================

- Fixed bug in setup file.

0.2 (Feb 7, 2007)
=================

Bugs Fixed
----------

- Non-empty log and run directories were deleated in un- and
  re-install.
