z3hello
=======

Introduction
============

This is a helloworld web application created using Zope packages. 

Installation
============

- Download and extract the tar ball::

    wget -c http://pypi.python.org/packages/source/z/z3hello/z3hello-0.3.tar.gz
    tar zxvf z3hello-0.3.tar.gz
    cd z3hello

- Run bootstrap.py::

    python2.6 bootstrap.py

- Run buildout::

    ./bin/buildout

- Run application::

    ./bin/paster serve deploy.ini

- Now access site at: http://localhost:8080/hello


Releases
========

0.3 (2010-01-01)
----------------

- No special instance recipe
- Use PasteDeploy

0.2 (2007-03-19)
----------------

Use zc.zope3recipes:app recipe

0.1 (2007-03-19)
----------------

Initial release of Zope 3 hello app.
