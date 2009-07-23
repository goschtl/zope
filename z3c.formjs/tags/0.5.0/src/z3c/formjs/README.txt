===========================
Form Javascript Integration
===========================

This package is designed to provide a Python API to common Javascript
features for forms written with the ``z3c.form*`` packages. While the
reference backend-implementation is for the JQuery library, any other
Javascript library can be hooked into the Python API.

The documents are ordered in the way they should be read:

- ``jsaction.txt`` [must read]

  This document describes how JS scripts can be connected to events on a
  any widget, inclduing buttons.

- ``jsvalidator.txt`` [must read]

  This document demonstrates how "live" widget value validation can be
  achieved.

- ``jsevent.txt`` [advanced users]

  This documents describes the generalization that allows hooking up script to
  events on any field.

- ``jqueryrenderer.txt`` [advanced users]

  This document demonstrates all necessary backend renderer components
  necessary to accomplish any of the features of this package.
