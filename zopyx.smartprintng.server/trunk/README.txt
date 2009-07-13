zopyx.smartprintng.server
=========================

A repoze.bfg based server implementation for the SmartPrintNG framework.
The SmartPrintNG server is part of the SmartPrintNG web-to-print solution
of ZOPYX.

Installation
============

- create an virtualenv environment (Python 2,4, 2.5 or 2.6)::

    virtualenv --no-site-packages .

- install ``repoze.bfg`` (by installing ``repoze.bfg.xmlrpc`` having ``repoze.bfg``
  as a dependency) ::

    bin/easy_install -i http://dist.repoze.org/bfgsite/simple repoze.bfg.xmlrpc

- install the SmartPrintNG server::

    bin/easy_install zopyx.smartprintng.server

- create a ``server.ini`` configuration file (and change according to your needs)::

    [DEFAULT]
    debug = true

    [app:main]
    use = egg:zopyx.smartprintng.server#app
    reload_templates = true
    debug_authorization = false
    debug_notfound = false

    [server:main]
    use = egg:Paste#http
    host = 127.0.0.1
    port = 6543

- start the server::

    bin/paster serve server.ini 

XMLRPC API
==========

The SmartPrintNG server exposes several methods through XMLRPC::

    def convertZIP(zip_archive, converter_name):
        """ 'zip_archive' is ZIP archive (encoded as base-64 byte string).
            The archive must contain exactly *one* HTML file to be converted
            including all related resources like stylesheets and images.
            All files must be stored flat within the archive (no subfolders).
            All references to externals resources like the 'src' attribute
            of the IMG tag or references to the stylesheet(s) must use
            relative paths.
        """

    def availableConverters():
        """ returns a list of available converter names on the 
            SmartPrintNG backend.
        """

    def ping():
        """ says 'pong' - or something similar """

Support
=======

Support for SmartPrintNG server is currently only available on a project basis.


Contact
=======

| ZOPYX Ltd. & Co. KG
| c/o Andreas Jung, 
| Charlottenstr. 37/1
| D-72070 Tuebingen, Germany
| E-mail: info at zopyx dot com
| Web: http://www.zopyx.com


