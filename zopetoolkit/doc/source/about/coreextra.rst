Core and Extra concepts
=======================

The Zope Toolkit covers only some libraries in the wider Zope
community and software repository. We introduce the concepts of *core*
and *extra* to be able to distinguish between the two.

Core libraries 
--------------

The Zope Toolkit is a set of libraries. These libraries are released
independently, but typically build on each other.

A library that at some point in time is considered to be part of the
Zope Toolkit is called a "core library". The Zope Toolkit contains
those libraries that are reused by a large number of projects, or that
the Zope Toolkit developers want to promote to be being more widely
adopted. The Zope Toolkit developers especially favor inclusions of
libraries that are used by other Zope projects.

The set of libraries that is "core" can change over time depending on
how these libraries evolve and are used. New libraries considered to
be "core" can be added to the set, and existing libraries once
considered "core" can be removed from the set.  We should be careful
though, as we cannot just drop libraries from the core without
considerable thought. A library being in the core signals a level of
commitment to this library.

How do we determine which libraries are part of the Zope Toolkit,
and which libraries are not? The set of Zope Toolkit libraries is
not static; what is included continuously evolves. The project
maintains a list of which libraries are considered core.

The Zope Toolkit Steering Group is the final arbiter of which
libraries are in Zope Toolkit or not. It will generally make decisions
according to these loose guidelines:

* if it's used widely in our community by the different consumer
  platforms, it's likely core.

* if it's used by only a single consumer platform, it's likely not
  core.

* if only a few people use it, it's likely not core.

* if it has a lot of people who contribute to it from our community,
  it's likely core.

* if it's something we want to encourage more consumer platforms use,
  it's likely core.

* if it contains specific user interface code, it's likely not
  core. If it contains code to help construct user interfaces however,
  it can be core.

Libraries may have a different status in the core to convey extra
information about them, such as deprecation status.

Reasons to consider refactoring packages, making dependencies optional
or removing a library from the ZTK are::

* if a library contains specific user interface code this makes it a
  candidate for splitting it into a reusable non-UI part and a UI part
  that is outside of the toolkit. If a library is UI focused it makes
  it a candidate for removal from the toolkit.

* if a library doesn't have narrative documentation and there is no
  commitment from maintainers to create such documentation. Naturally
  critical libraries with a lot of use won't just removed for this reason,
  but this should also be a good motivator to add documentation.

* if a library depends on another library maintained in the Zope
  repository that is itself not in the core we should think about
  removing this dependency or making the dependency optional. Another
  possibility is to remove the library that has this dependency from
  the toolkit altogether, or to adopt the dependency itself into the
  toolkit.

Extra libraries
---------------

Surrounding the Zope Toolkit core libraries a large number of other
libraries exist that are developed in association with the Zope
Toolkit. These libraries integrate with the Zope Toolkit and make
use of the Zope Toolkit. They are often maintained by developers
that are also Zope Toolkit developers, and similar development
practices are used.

We will call these libraries "extra". Libraries in the extra group are
sometimes candidates for inclusion in the core, or might be libraries
formerly part of the core but still being maintained. In general some
development philosophies and practices will be shared between the core
and extra group of libraries.

The Zope Toolkit steering group *does* not control the development
of the extra libraries in the repository, except where such a library
is considered for adoption within the Zope Toolkit itself as a core
library.

Examples of "extra" libraries are the "hurry.query" library for
constructing catalog queries, the "z3c.form" related libraries for
form generation, and the "grokcore.component" library which contains a
different way to configure components.

Any library that is developed for integration with the Zope Toolkit
in the Zope repository can be considered "extra"; "extra" is the set
of libraries that is not in the Zope Toolkit but can work with it. By 
having an "extra" designation we can more easily discuss such libraries.
