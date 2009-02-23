Setting Up Virtual Hosting
==========================

Introduction
------------

One of the most common tasks in the Zope world is to hide Zope behind
the Apache web server in order to make use of all the nice features
Apache provides, especially SSL encryption.

Configuration
-------------

Apache and other Web servers are commonly connected to Zope via
rewrite rules specified in virtual hosts.  Zope needs to interpret
these requests correctly and provide meaningful output.  You might
think this is easy because you just have to point to the right URL of
the Zope server.  But this is only half the story.  What about a URL
that points to another object?  To handle that situation, you need to
tell Zope what the true virtual hosting address is.  In Zope 3 this
is accomplished using a special namespace called `vh`, which
specifies the public address.

Before you can start setting up a virtual hosting environment on your
server, you need to do the following:

1. Make sure Zope 3 is running at http://localhost:8080/site/ or more
   generically at http://destinationurl:port/path-to-site/.

2. Make sure Apache is running at http://www.example.com:80/ or more
   generically at http://publicurl:port/

Zope 3 uses its URL namespace capability to allow virtual hosting, so
that no special component or coding practice is required, which means
virtual hosting is always available.  Generally, namespaces are
specified using `++namespace++` as one element of the URL.  For the
`vh` namespace, for example, you have `++vh++Public-URL++`. The `++`
at the end of the URL is specific to the vh namespace.  It signals
the end of the public URL.

The namespace approach has the advantage that you can never lock
yourself out due to misconfiguration.  Some Zope 2 virtual hosting
solutions have this problem and cause unnecessary headaches.  In Zope
2 you also have to add an additional object.  Zope 3 does not use any
service or utility for this task, which makes virtual hosting support
a very core functionality.

However, from an Apache 1.3 point of view, the setup of Zope 3 is
very similar to that of Zope 2.  In the httpd.conf file--usually
found somewhere in /etc or /etc/httpd--you insert the following
lines::

  Listen 80
 
  <VirtualHost *:80>
    ServerAdmin guest@example.com
    RewriteEngine On
    RewriteLog /path/to/rewrite.log
    RewriteLogLevel 9
    RewriteRule ^/(/?.*) \
      http://localhost:8080/++vh++http:example.com:80/++/$1 [P,L]
   </VirtualHost>

In the preceding code block, note the following:

* Line 1: You set up the Apache server for the default port 80.
* Line 3: You declare all incoming requests on port 80 as virtual
  hosting sites.
* Lines 4-10: These are all specific configuration instructions for
  the virtual host at port 80.
* Line 9: The virtual host is known as www.example.com to the outside
  world.
* Line 7: You define the location of the error log.
* Line 10: You turn on the Rewrite Engine, basically telling Apache
  that this virtual host will rewrite and redirect requests.
* Line 11-13: The code in these lines should really appear on one
  line. It defines the actual rewrite rule, which says If you find
  the URL after the hostname and port to begin with /site, then
  rewrite this URL to
  http://localhost:8080/site/++vh++http:www.example.com:80/site/++
  plus whatever was behind /site.  For example,
  www.example.com:80/site/hello.html is rewritten to
  http://localhost:8080/site/++vh++http:www.example.com:80/site/++/hello.html.

Note that the part after `++vh++` must strictly be of the form
`(protocol):(host):(port)/(path)` Even if the port is 80 (the
default), you have to specify it.

At this point you are done setting up Apache.  It's easy, isn't it?
All you need to do now is restart Apache so that the changes in
configuration will take effect.

Nothing special needs to be configured on the Zope 3 side.  Zope is
actually totally unaware of the virtual hosting setup.  Note that you
do not have to map the URL www.example.com/ to `localhost:8080/`; you
can choose any location on the Zope server you like.

You can now combine the preceding setup with all sorts of other
Apache configurations as well (for example, SSL).  You just use port
443 instead of 80 and enable SSL.

Note: One of the current problems in Zope 3 is that the XML
navigation tree in the management interface does not work with
virtual hosting because of the way it treats a URL.
