Overview
========

ZNagios provides the ability for Nagios and munin to tap into the Zope2 server
and retrieve status and performance data.

Nagios data
-----------

- uptime
- main database size
- total reference count
- errors in the root error log

Munin data
----------

XXX

Configure Nagios
----------------

Put a line like this in your nagios plugin configuration to make the plugin
available::

  command[check_zope]=/path/to/check_zope.py -H $ARG1$ -p $ARG2$ -d $ARG3$
  -r $ARG4$ -a $ARG5$

Put a line like this in your nagios host configuration to use the::

  service[maggie]=Zope;0;24x7;10;5;5;gocept;10;24x7;1;1;1;;check_zope!localhost!8080!50000000!10000!admin:password

Configure Nagios
----------------

To get the correct command configuration for "check_zope", copy the zope.cfg
into your plugin config directory (debian: /usr/share/nagios/pluginconfig) or
the commands.cfg in /etc/nagios/.

Then you can make use of the check_zope command for services::

  define service{
              use                     generic-service
              host_name               thezopehost
              service_description     Zope
              check_command           check_zope!thezopehost!8080!1000000000!500000!admin:password
  }

Credits
-------

Originally written by Christian Theune <ct at gocept dot com>.

Thanks for contributing ideas and code to:

- Robrecht van Valkenburg (Pareto)
- Martijn Pieters (Pareto)
- Florian Schulze (independent)
- Hanno Schlichting (Jarn)
