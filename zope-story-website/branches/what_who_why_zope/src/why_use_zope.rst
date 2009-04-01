Why Use Zope?
=============

Zope applications, libraries, and frameworks are suited for different purposes
and environments; each has a set of strengths and weaknesses.

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
developer productivity by avoiding the complexity of a relational database
layer.

However, relational databases (RDBMs) are also a popular persistence option
for Zope applications, and good options exist for using object relational
mappers such as SQLAlchemy and Storm.

Zope Component Architecture (ZCA)
---------------------------------

One of the lessons learned over the years was the need for a component
architecture; using object composition instead of object inheritance avoids
tight coupling between application parts so that components can be swapped
without causing breakage. The Zope Component Architecture provides and elegant
solution which helps manage complexity and encourage component reusability.


RDBMs
