Thoughts for a Zope 4 ZMI
=========================

Assumptions and scope
---------------------
The following points are not meant as exact definitions, they are more
of a brain dump and starting point:

* The ZMI is meant to support administering and developing Zope
  applications, especially server-side debugging and introspection.

* The ZMI is not meant as a generic UI for administering applications
  or entering/editing data in an application.

* Request debugging by interception of application requests is not a
  goal, but the ZMI can support integration of such tools.

* Day to day application administration tasks should never be dependent
  on having the new ZMI around. Applications must remain usable without it.

* The ZMI must always function when needed, even if an application's own
  views are broken.

* The ZMI is not meant to provide full backwards compatibility with
  the old Zope 2 ZMI.


Use cases, functions and desirable views
----------------------------------------
* ZODB (Caches, Connections, ...)

* ZODB browsing (selection of attributes, readability, "broken" objects).
  This needs UI TLC to become/stay usable, and documentation of underlying
  concepts and goals to enable future development

* ZODB history

* ZODB transaction log

* relational databases (SQLAlchemy, ZSQL),

* Zope process parameters

* Other configuration parameters (read and experiment with them)

* interactive interpreter (e.g. to set attributes, including transaction
  integration)

* profiler

* Zope 3 components without their own UI (generations, registry
  introspection, etc)

* code browser??

* PropertyManager or alternatives?

* error log (Zope Site Error Log)

* long request log

* offline support (dumping configurations, parameter, etc)

* single request debugging (request logs with complete request/response
  information, performance stats, profiling, other code logging output,
  post-mortem debugging (like WebError). This can potentially be extended
  by application-specific debugging information. This kind of debugging
  should be enabled from the ZMI and singe request overlay mechanisms
  should be available alongside a central UI.

* content adding is application-specific. The question what support
  to offer from the ZMI is not solved.


Unsupported use cases
---------------------
* generic CRUD/BREAD


Non-functional requirements
---------------------------
* The ZMI should be resilient in the face of application issues ("broken"
  objects, application errors, missing filesystem code)

* simple code

* generic UI (like SmallTalk), but no attempt at "one size fits all" like
  Plone

* easy pluggability for additional ZMI views

* separation of UI and code to ease refactoring of DTML-dependent code

* as little dependencies as possible beyond the Zope egg and its dependencies


Implementation thoughts
-----------------------
* minimal boilerplate: O-Wrap, Tree, menu system?

* separate skin (++skin++zmi)

* generic object traversal independent of URL space and application code

* the views should have as few dependencies (e.g. form library
  dependencies) as possible. It should run without requiring extra
  installation or configuration steps past installing the egg and
  calling up the views.

* translations are supported by wrapping user-visible messages as
  TranslationStrings in a shard translation domain ("zmi").

* HTML should be cleaned up when writing new views, preferably using HTML 5
  semantics.

Starting points
---------------
* current Zope 2 ZMI views

* methods in Zope or add-on products that support the old ZMI

* plone.app.debugtoolbar / pyramid toolbar

* Smalltalk UI


Current ZMI views brainstorming
-------------------------------
* It's not clear how to convert the "Add list" in the old ZMI. The new
  ZMI may have to provide a way to register "addable" items.

* The "Contents" tab is application-specific. Its replacement is a
  more generic object browser.

* It's not clear how to handle "virtual" items that don't really exist in
  the database, such as the ''/temp_folder''

* The "View" tab is useful for developers, they can jump to the public
  view for an object.

* The PropertyManager "Properties" tab is an older Zope 2 API with an
  unclear future status. Most developers have moved to store attributes
  in a different way, meaning their owbjects provide built-in views
  for them already.

* The "Security" tab will continue to be available as a "read only" view
  to show a security profile for the given context. It should retain the
  current functionality of allowing user name input to show rights for
  specific user accounts for the given context.

* The "Undo" tab will remain; having some ZODB transaction log is already
  in scope for the new ZMI.

* The "Security" tab replacement can also take over what the "Owner" tab
  does now, meaning it should the "executable" owner as well.

* The "Interfaces" tab will remain but lose the ability to add marker
  interfaces for an object which is an application-specific setting.
  Only the application knows what such interfaces mean.

* The "Find" tab should become part of the object browser.

* "Edit" tabs are application-specific, they must be provided by the
  applicaton developer.

* The "Proxy" tab for setting proxy roles on an object will not be
  supported.

* "History" is an application-specific tab, so it's not part of the
  core package.

* Nearly all views from the Control_Panel should be reimplemented as
  part of a new ZMI.


