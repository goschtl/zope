Example of Zope 3 without the ZODB
==================================

This is an excruciatingly simple example Zope3 application that does not use
the ZODB.

To test it, copy the zodbless_zope.conf and simple_site.zcml to the top
directory of a zope checkout.

Start the zope server with ./z3.py -C zodbless_zope.conf

Then go to http://localhost:8080/index.html
