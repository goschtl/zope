===================================================
A Framework for Building RESTive Services in Zope 3
===================================================

This package implements several components that relate to building RESTive Web
services using the Zope publisher. Each set of components is documented in a
corresponding text file.

* ``client.txt`` [must read]

  This package also provides a REST Web client, which can be used for testing
  or for accessing a RESTive API within an application.

* ``null.txt`` [advanced user]

  In order to create new resources, the publisher must be able to traverse to
  resources/objects that do not yet exist. This file explains how those null
  resources work.

* ``traverser.txt`` [advanced user]

  The ``traverser`` module contains several traversal helper components for
  common traversal scenarios, suhc as containers and null resources.

* ``rest.txt`` [informative]

  This document introduces the hooks required to manage RESTive requests in
  the publisher. It also discusses hwo those components are used by the
  publisher.
