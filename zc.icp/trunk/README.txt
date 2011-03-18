====================================
Internet Cache Protocol (ICP) Server
====================================

In multi-machine (or multi-process) web server installations some set of web
servers will likely be more able to quickly service an HTTP request than
others.  HTTP accelerators (reverse proxies) like Squid_ can use ICP_ queries
to find the most appropriate server(s) to handle a particular request.  This
package provides a small UDP server that can respond to ICP queries based on
pluggable policies.

.. [ICP] http://www.faqs.org/rfcs/rfc2186.html
.. [Squid] http://www.squid-cache.org/
