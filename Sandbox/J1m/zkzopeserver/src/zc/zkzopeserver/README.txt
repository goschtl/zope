=================================================
zope.server wrapper that registers with ZooKeeper
=================================================

``zc.zkzopeserver`` provides a wrapper for the zope.server WSGI runner
that registers with ZooKeeper.  By registering with ZooKeeper, you can
let the operating system assign ports and have clients find your
server by looking in ZooKeeper.

Basic Usage
===========

The wrapper is used in a past-deply configuration file::

   [server:main]
   use = egg:zc.zkzopeserver
   zookeeper = zookeeper.example.com:2181
   path = /fooservice/providers

.. -> server_config

The wrapper supports the following options:

zookeeper
   required ZooKeeper connection string

path
   required path at which to register your server.

   Your server is registered by adding a ZooKeeper ephemeral node as a
   child of the path with the server address as the name.

host
   host name or ip to listen on, defaultiong to ''

port
   The port to listen on, defaulting to 0

session_timeout
   A ZooKeeper session timeout in milliseconds

threads
   The size of the thread pool, defaulting to 1

.. test

    >>> import ConfigParser, StringIO
    >>> parser = ConfigParser.RawConfigParser()
    >>> parser.readfp(StringIO.StringIO(server_config))
    >>> kw = dict(parser.items('server:main'))

    >>> import pkg_resources
    >>> dist = kw.pop('use').split(':')[1]
    >>> [run] = [v.load()
    ...          for v in pkg_resources.get_entry_map(
    ...                 'zc.zkzopeserver', 'paste.server_runner'
    ...                  ).values()]

    >>> import wsgiref.simple_server, zc.thread
    >>> @zc.thread.Thread
    ... def server():
    ...     run(wsgiref.simple_server.demo_app, {}, **kw)

    >>> import time
    >>> time.sleep(.1)

    >>> import urllib, zc.zk
    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')

    >>> [port] = [int(c.split(':')[1])
    ...           for c in zk.get_children('/fooservice/providers')]
    >>> print urllib.urlopen('http://127.0.0.1:%s/' % port).read()
    ... # doctest: +ELLIPSIS
    Hello world!
    ...

    Cleanup, sigh, violently close the server.

    >>> import asyncore
    >>> for s in asyncore.socket_map.values():
    ...     s.close()
    >>> server.join(1)
    >>> zk.close()



Change History
==============

0.1.0 (2011-12-??)
------------------

Initial release
