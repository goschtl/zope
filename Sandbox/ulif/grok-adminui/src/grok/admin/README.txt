=====================
A basic grok admin UI
=====================

The internal name of the admin UI is:
Grok Application Interface Application or, for short gaia.

Overview
--------

* List of all instanciated applications (grouped by application?)

* "Add new application" form: drop down for selecting the application
   and a field for the id.

* "Delete application" form: checkboxes displayed with listed installed
  applications. Selected items may be deleted.


TODO:
-----

Layout/Design/Templates:
........................

* Get rid of garbage in docgrok-views

* Get a new layout

* Rename topics:

  - z3index -> server

  - appsindex -> applications

* AJAXification using some framework (MojiKit or KSS most probably)


Functional:
...........

* Debugging

  - Debugger

  - Error Logs, usable for developers

* Profiling

* Object browser / Introspection tool

  - Give information concerning installed apps, their containers
    and contained objects.

* Better application handling

  - Configure apps.

* Display hints for where to find username / password for new users

* Login/Logout(?)

* Display username(?)

* Error Messages:

  - Give message, when input errors (no appname given etc.) occur

  - Customizable error pages(?)
