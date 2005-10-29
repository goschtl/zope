A cx_Oracle based Database Adapter for Zope3

Home: http://www2.staff.fh-vorarlberg.ac.at/~bd/

Installation

 1. Install the cx_Oracle python package from
    http://sourceforge.net/projects/cx-oracle/

 2. Place this directory somewhere in your PYTHONPATH

 3. Place the file 'cxoracleda-configure.zcml' into your package-includes
    directory of your zope instance.


DSN Usage:

 If a DSN specifies a host then it is assumed that the dbname is an
 Oracle SID and an Oracle DSN is created with this SID. (see
 cx_Oracle.makedsn)

 If no host is defined in the DSN, then it is assumed, that dbname is
 the name of a local TNS Entry.
