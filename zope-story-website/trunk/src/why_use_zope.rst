.. role:: header
.. role:: zsection

.. container::
   :class: menuacross

   + `What is Zope? <index.html>`_
   + `Who is Zope? <who_is_zope.html>`_
   + `Why Zope? <why_use_zope.html>`_
   

Why Use Zope?
=============

Zope applications, libraries, and frameworks are suited for different purposes
and environments; but most share common advantages:

Zope is Mature
--------------

Zope's robust technologies are born of 10 years of hard-won real world
experience in building production web applications for every level of
organization, ranging from small nonprofits to large enterprise systems and
high traffic public web applications.

Zope's groundbreaking innovations over the years led the way in demonstrating
the practicality of powerful software patterns, including object databases,
object publishing, and component architecture.

All the applications built using the Zope Framework benefit from this
maturity, For example, the older projects, the Zope 2 app server as well as
Plone, both increasingly make use of the newest Zope library versions while
still maintaining the feature set that makes it useful in heavy production
settings.

Meanwhile, younger Zope web frameworks such as Grok and Repoze.BFG, leverage
the mature Zope Framework libraries to bring new ideas to web development.

Designed for Automated Testing
------------------------------

All the major Zope frameworks and libraries are built around a culture of
automated testing.

Scalable Performance
--------------------

Applications built using the Zope Object Database can benefit from ZEO
Clustering, which allow multiple applications to share a single object
database.

Persistence Options
-------------------

Zope applications traditionally benefit from the use of a mature
high-performance transactional object database called ZODB, which increases
developer productivity by avoiding the management overhead of a relational
database layer. This benefit multiplies when combined with Zope schema classes
to marry content objects and metadata with web forms.

However, relational databases (RDBMs) are also a popular persistence option
for Zope applications, and good options exist for using object relational
mappers such as SQLAlchemy and Storm. 

See also:
    + `ZODB in Python Package Index`_
    + `ZODB/ZEO Programming Guide`_
    + `ZODB vs Relational Database: a simple benchmark`_
    + `SQLAlchemy`_
    + `Storm`_

Zope Component Architecture (ZCA)
---------------------------------

One of the lessons learned over the years was the need for a component
architecture; using object composition instead of object inheritance avoids
tight coupling between application parts so that components can be swapped
without causing breakage. The Zope Component Architecture provides and elegant
solution which helps manage complexity and encourage component reusability.

See also:
    + `A Comprehensive Guide to Zope Component Architecture`_
    + `Zope Component Architecture Overview`_
    + `Grok Explains Zope Component Architecture`_

Security
-------------------

The `Zope Framework`_ offers significant security advantages in the form of
a fine-grained and highly manageable infrastructure, including support
for pluggable authentication and permission-based security policies for object
publishing, down to the level of methods and attributes. 

By default, nothing is published unless an explicit security declaration is
attached either within application code or within configuration.

For applications needing less security and more simplicity, Zope Framework
security can be relaxed to allow convenient, free-form web object publishing.

When it comes to security, one size does NOT fit all.

See also:
    + `Pluggable Authenication for Plone and Zope 2 <http://plone.org/documentation/manual/pas-reference-manual/referencemanual-all-pages>`__


MetaData and Dublin Core
-------------------------

Zope supports attaching metadata for application content objects, adhering
to the `Dublin Core <http://dublincore.org/>`_ metadata standard.


I18n and L10n Support
-------------------------------------------------------------

`Zope Framework`_ supports a manageable approach to internationalization and
localization, to make Zope applications easily translatable.


Twisted Server Integration
---------------------------

While Zope does have a robust built-in HTTP server for publishing objects to
the web, it also comes bundled with the powerful `Twisted`_ server, an 
"event-driven networking engine" designed to support not only HTTP but
many other network protocols in a concurrently asynchronous fashion.


WSGI Integration Options
---------------------------

Zope plays well with `WSGI`_ HTTP pipelines, enabling layering
of `WSGI "middleware"`_ applications between the web server and the main
"endware" application. Zope applications can play the role of either
WSGI middleware or endware.

See also:
    + `Repoze: Integrating Zope Into a WSGI World`_
    + `PasteDeploy`_




.. _`Zope Framework`: http://docs.zope.org/zopeframework/
.. _`WSGI`: http://wsgi.org/wsgi/
.. _`WSGI "middleware"`: http://wsgi.org/wsgi/Middleware_and_Utilities
.. _`Twisted`: http://twistedmatrix.com/trac/wiki
.. _`PasteDeploy`: http://docs.zope.org/zope3/Code/zope/publisher/paste.txt/index.html
.. _`Repoze: Integrating Zope Into a WSGI World`: http://repoze.org/about.html
.. _`ZODB vs Relational Database: a simple benchmark`: http://pyinsci.blogspot.com/2007/09/zodb-vs-relational-database-simple.html
.. _`ZODB/ZEO Programming Guide`: http://wiki.zope.org/ZODB/guide/index.html
.. _`ZODB in Python Package Index`: http://pypi.python.org/pypi/ZODB3
.. _`SQLAlchemy`: http://www.sqlalchemy.org/
.. _`Storm`: https://storm.canonical.com/
.. _`A Comprehensive Guide to Zope Component Architecture`: http://muthukadan.net/docs/zca.html
.. _`Zope Component Architecture Overview`: http://wiki.zope.org/zope3/ComponentArchitectureOverview
.. _`Grok Explains Zope Component Architecture`: http://grok.zope.org/about/component-architecture