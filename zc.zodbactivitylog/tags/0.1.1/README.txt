***********************
ZODB Activity Log
***********************

XXX Need tests!

This package provides an activity log that lets you track database
activity.  

Just:

- put the package in your path 

- Add::

    <include package="zc.zodbactivitylog" />

  to your ZCML

- Add a log entry to your zope.conf:

  ::
    <logger>
       name zc.zodbactivitylog
       propagate false

      <logfile>
        path ${buildout:directory}/zodb.log
        format %(asctime)s %(message)s
      </logfile>
    </logger>
  
  setting the path option appropriately.

There is an output log entry for each connection.  Each entry has a
time, a number of reads, and a number of writes.

XXX The log entries don't contain database names.  This package will
need to be updated for multiple databases.  Maybe I'll do that when I
write tests.


Changes
*******

0.1 (yyyy-mm-dd)
================

Initial release
