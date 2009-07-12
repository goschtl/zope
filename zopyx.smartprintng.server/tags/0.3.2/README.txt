zopyx.smartprintng.server
=========================

A repoze.bfg based server implementation for the SmartPrintNG framework.


Installation
============

- create an virtualenv environment (Python 2,4, 2.5 or 2.6)::

    virtualenv --no-site-packages .

- install ``repoze.bfg`` (by installing ``repoze.bfg.xmlrpc`` having ``repoze.bfg``
  as a dependency) ::

    bin/easy_install -i http://dist.repoze.org/bfgsite/simple repoze.bfg.xmlrpc

- install the SmartPrintNG server::

    bin/easy_install zopyx.smartprintng.server

- create a ``server.ini`` configuration file::

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
    bin/python setup.py develop

- start the server::

    bin/paster serve server.ini 


Contact
=======

| ZOPYX Ltd. & Co. KG
| c/o Andreas Jung, 
| Charlottenstr. 37/1
| D-72070 Tuebingen, Germany
| E-mail: info at zopyx dot com
| Web: http://www.zopyx.com


