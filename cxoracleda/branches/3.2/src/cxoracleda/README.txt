============================================
A cx_Oracle based Database Adapter for Zope3
============================================

:Source Repository: http://svn.zope.org/cxoracleda/trunk/

Note that this package does not work with Zope 2. If you are looking
for a Zope 2 cx_Oracle based DA, you can find it at
http://www.zope.org/Members/evrimozcelik/zxoracleda.

Installation
============

1. Install the cx_Oracle python package from
   http://sourceforge.net/projects/cx-oracle/

2. Place this directory somewhere in your PYTHONPATH

3. Place the file 'cxoracleda-configure.zcml' into your
   package-includes directory of your zope instance.

DSN Usage
=========

If a DSN specifies a host then it is assumed that the dbname is an
Oracle SID and an Oracle DSN is created with this SID. (see
cx_Oracle.makedsn)

If no host is defined in the DSN, then it is assumed, that dbname is
the name of a local TNS Entry.
