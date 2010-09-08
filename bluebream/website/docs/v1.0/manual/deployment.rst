.. _man-deployment:

Deployment
==========

Introduction
------------

BlueBream provides a WSGI application which can be run on any `WSGI server
<http://wsgi.org/wsgi/Servers>`_.  This chapter will explain using a WSGI
server called `gunicorn <http://gunicorn.org/>`_ together with `nginx
<http://wiki.nginx.org/Main>`_ as a `reverse proxy
<http://wiki.nginx.org/NginxHttpProxyModule>`_ to deploy BlueBream.  For
general information, refer the `gunicorn deployment documenation
<http://gunicorn.org/deploy.html>`_.

Installing and setting up gunicorn
----------------------------------

The gunicorn is available in Python egg format from PyPI.  To install, you
can include ``gunicorn`` in the list of eggs inside the ``[app]`` part.  If
you are working on the ``ticketcollector`` example application, you can
include ``gunicorn`` in ``eggs`` list.  Open the ``buildout.cfg`` file and
update the ``[app]`` part like this::

  [app]
  recipe = zc.recipe.egg
  eggs = ticketcollector
         z3c.evalexception>=2.0
         Paste
         PasteScript
         PasteDeploy
         gunicorn
  interpreter = bbpy

After updating Buildout configuration, you need to run the
``./bin/buildout`` command.  This will download and install ``gunicorn``.

If you look at the ``deploy.ini`` file, you can see that the WSGI server
provided by ``Paste`` package is used by default.  The WSGI server section
will be configured like this::

  [server:main]
  use = egg:Paste#http
  host = 127.0.0.1
  port = 8080

You need to change this line::

  use = egg:Paste#http

with::

  use = egg:gunicorn#main

The updated ``[server:main]`` section will look like this::

  [server:main]
  use = egg:gunicorn#main
  host = 127.0.0.1
  port = 8080

You can start the WSGI server like this::

  ./bin/paster deploy.ini --daemon

And stop the WSGI server like this::

  ./bin/paster deploy.ini --stop-daemon

Configuring nginx as reverse proxy
----------------------------------

::

  worker_processes 1;

  user nobody nogroup;
  pid /tmp/nginx.pid;
  error_log /tmp/nginx.error.log;

  events {
      worker_connections 1024;
      accept_mutex off;
  }

  http {
      include mime.types;
      default_type application/octet-stream;
      access_log /tmp/nginx.access.log combined;
      sendfile on;

      upstream app_server {
          server 127.0.0.1:8080 fail_timeout=0;
      }

      server {
          listen 80 default;
          client_max_body_size 4G;
          server_name _;

          keepalive_timeout 5;

          # path for static files
          root /path/to/app/current/public;

          location / {
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header Host $http_host;
              proxy_redirect off;

              if (!-f $request_filename) {
                  rewrite ^/(.*)$ /site/++vh++http:domain.com:80/++/$1 break;
                  proxy_pass http://app_server;
                  break;
              }
          }

          error_page 500 502 503 504 /500.html;
          location = /500.html {
              root /path/to/app/current/public;
          }
      }
  }

You need to update this line::

 rewrite ^/(.*)$ /site/++vh++http:domain.com:80/++/$1 break;

The ``site`` is the site you need to use.  For example, if you installed
ticket collector in a ``tc`` folder and configured it as a :ref:`local site
<howto-local-site-manager>`, use ``tc`` as the site.

The ``domain.com`` should be changed to whatever domain you configured.
If the domain is example.com, the rewrite rule will look like this::

 rewrite ^/(.*)$ /tc/++vh++http:example.com:80/++/$1 break;

You can start Nginx after configuring.  The application will be available at
http://example.com/ .

Conclusion
----------

This chapter explained deploying BlueBream application using gunicorn and
Nginx.
