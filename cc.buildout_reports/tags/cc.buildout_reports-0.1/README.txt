****************
Buildout Reports
****************

.. contents::

cc.buildout_reports provides recipe[s] for generating developer reports 
using zc.buildout.  

XXX/TODO Report
***************

The cc.bulidout_reports:xxx recipe can be used to scan a project for comments
flagged with a specifed pattern (XXX|TODO by default).  The recipe does not
scan temporary files (``*~``) or traverse into ``egg`` and ``.svn`` 
directories.

The recipe supports two optional parameters:

pattern
    The pattern to scan for; if not specified, defaults to ``(XXX|TODO)``.
        
report_file
    The file to save the report to; if not specified, defaults
    to ``XXXreport.html``, stored in the buildout directory.  If specified
    as a relative path, it is interpreted as relative to the buildout
    directory.
