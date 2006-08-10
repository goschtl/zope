===================
Filestorage Package
===================

This package offers large file handling solutions for zope3. The first
implementation is based on properties, the second on wsgi. The
property implementation runs on plain zope 3.

This is work in progress: see todo.txt

Property
========

Installation
------------

Define an evnironment variable in your runzope like this::

 os.environ['EXTFILE_STORAGEDIR'] = '/tmp/filestorage'

This causes a IHashDir utilitiy to be registered upon zope startup.

see hashdir.txt, property.txt

WSGI (optional)
===============

This package provides a wsgi filter that upon upload replaces the
content of the upload with the sha digest of the content and stores
the file on the filesystem. Upon download it looks if it has a digest
and returns the according file directly from the filesystem.

See also: hashdir.txt, processort.txt

This package is currently only tested with zope3 twisted server.

Requirements
============

Zope 3 with twisted server, this package does not work with zserver.

:zope.paste: follow the instructions in
http://svn.zope.org/zope.paste/trunk/README.txt

Installation
============

Add the following to instance_home/etc/paste.ini. The directory
parameter defines the storage directory for files.

Example paste.ini::

 [pipeline:Paste.Main]
 pipeline = fs main
 
 [app:main]
 paste.app_factory = zope.paste.application:zope_publisher_app_factory
 
 [filter:fs]
 paste.filter_factory = z3c.extfile.filter:filter_factory
 directory = /path/to/hashdir/storage

