.. _faq-faq:

FAQ
===

.. contents::

.. _faq-general:

General
-------

What is BlueBream ?
~~~~~~~~~~~~~~~~~~~

BlueBream is a **production ready** free/open source web application
framework written in the Python programming language.  BlueBream provides a
component architecture, transactional object database, tightly integrated
security model and many other features.

BlueBream is coming from the Zope community which is started around 1998.
Initially Zope's core technologies were designed by Zope Corporation.  The
development of BlueBream started in late 2001.  In November 2004, BlueBream
was released.  BlueBream is a complete rewrite that only preserves the
original ZODB object database.  The design of BlueBream is driven by the
needs of large companies.  It is directly intended for enterprise web
application development using the newest development paradigms.  Extreme
programming development process has a real influence in BlueBream
development.  Automated testing is a major strength of BlueBream.  Sprints_
were introduced to help accelerate BlueBream development.  In 2006 `Zope
foundation`_ was formed to help organize and formalize the relationships
with the Zope community.

.. _Sprints: http://www.zopemag.com/Guides/miniGuide_ZopeSprinting.html
.. _Zope foundation: http://foundation.zope.org
.. _subversion: http://svn.zope.org/

Why BlueBream ?
~~~~~~~~~~~~~~~

A few features distinguish BlueBream from other Python web frameworks.

- BlueBream is built on top of the :term:`Zope Tool Kit` (ZTK), which has
  many years of experience proving it meets the demanding requirements for
  stable, scalable software.

- BlueBream uses the powerful and familiar :term:`Buildout` system written
  in Python.

- BlueBream employs the Zope Object Database (:term:`ZODB`), a transactional
  object database providing extremely powerful and easy to use persistence.

- BlueBream registers components with Zope Component Markup Language
  (:term:`ZCML`), an XML based configuration language, providing limitless
  flexibility.

- BlueBream can also register components using :term:`GROK`, which adds a
  layer replacing the declarative configuration of ZCML with conventions and
  declarations in standard Python.

- BlueBream features the :term:`Zope Component Architecture` (ZCA) which
  implements :term:`Separation of concerns` to create highly cohesive
  reusable components (zope.component_).

- BlueBream implements Python Web Server Gateway Interface :term:`WSGI`
  using :term:`Paste`, :term:`PasteScript`, and :term:`PasteDeploy`.

- BlueBream includes a number of well tested components to implement common
  activities.  A few are of these are:

  - zope.publisher_ publishes Python objects on the web, emphasizing
    :term:`WSGI` compatibility

  - zope.security_ provides a generic mechanism for pluggable security
    policies

  - zope.testing_ and zope.testbrowser_ offer unit and functional testing
    frameworks

  - zope.pagetemplate_ is an XHTML-compliant language for devloping
    templates

  - zope.schema_ is a schema engine

  - zope.formlib_ is a tool for automatically generating forms

BlueBream is free/open source software, owned by the :term:`Zope
Foundation`.  Bluebream is licensed under the :term:`Zope Public License`
(BSD like, GPL compatible license).

.. _zope.component: http://pypi.python.org/pypi/zope.component
.. _zope.publisher: http://pypi.python.org/pypi/zope.publisher
.. _zope.security: http://pypi.python.org/pypi/zope.security
.. _zope.testing: http://pypi.python.org/pypi/zope.testing
.. _zope.testbrowser: http://pypi.python.org/pypi/zope.testbrowser
.. _zope.pagetemplate: http://pypi.python.org/pypi/zope.pagetemplate
.. _zope.schema: http://pypi.python.org/pypi/zope.schema
.. _zope.formlib: http://pypi.python.org/pypi/zope.formlib

What is the Zope Foundation ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From http://foundation.zope.org::

  The Zope Foundation has the goal to promote, maintain, and develop the
  Zope platform.  It does this by supporting the Zope community.  Our
  community includes the open source community of contributors to the Zope
  software, contributors to the documentation and web infrastructure, as
  well as the community of businesses and organizations that use Zope.

  The Zope Foundation is the copyright holder of the Zope software and many
  extensions and associated software.  The Zope Foundation also manages the
  zope.org website, and manages the infrastructure for open source
  collaboration.

For more details: http://foundation.zope.org/about


How can I help ?
~~~~~~~~~~~~~~~~

If you're interested in helping and you have time, educate yourself on the
component architecture and BlueBream then volunteer to assist in your
particular area of expertise.  Please come to our IRC channel: #bluebream at
irc.freenode.net Also join the mailing list:
https://mail.zope.org/mailman/listinfo/bluebream There is a wiki page with
more details: http://wiki.zope.org/bluebream/ContributingToBlueBream

What is the license of BlueBream ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BlueBream is licensed under :term:`Zope Public License` (BSD like, GPL
compatible license).

Is BlueBream stable enough to be used in production environment ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, it is stable enough to be used in production environment.  BlueBream
(or old Zope 3) is used in several larger production sites already.  Several
custom solutions have been written too.  But the development of BlueBream
will probably never be done, it will continue until all our needs are met :)

Which Python version is required?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BlueBream 1.0 support the following Python versions on 32 bit platforms:

- Python 2.4
- Python 2.5
- Python 2.6

If you are using 64 bit platform, it is recommended to use Python 2.6 with
BlueBream.

The supported operating systems are: GNU/Linux & MS Windows

What is the KGS (Known Good Set) ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting from version Zope 3.4, Zope 3 (BlueBream) has been split into many
packages called "eggs", that are released independently.  The KGS is a set
of python eggs, that are known to work together listed as a Buildout version
file.

* The KGS package index for zope 3.4 is : http://download.zope.org/zope3.4/

New versions file will be available here:
http://download.zope.org/bluebream/

How do I start a new BlueBream project ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please look at the :ref:`started-getting` documentation.

.. _faq-concepts:

Concepts
--------

What is the component architecture ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's similar to other component architectures in that it lets you fit small
pieces of functionality together.  The Zope component architecture is built
on top of :ref:`interface <man-interface>` concept.  You can read more about
component architecture in the :ref:`manual <man-zca>`.

Where can I find pointers to resources ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `Official Site <http://bluebream.zope.org>`_

- `Wiki <http://wiki.zope.org/bluebream>`_.

- `PyPI Page <http://pypi.python.org/pypi/bluebream>`_

- `Mailing List <https://mail.zope.org/mailman/listinfo/bluebream>`_

- `Twitter <http://twitter.com/bluebream>`_

- `Blog <http://bluebream.posterous.com>`_

- IRC Channel: `#bluebream at freenode.net <http://webchat.freenode.net/?randomnick=1&channels=bluebream>`_

- Ohloh.net: https://www.ohloh.net/p/bluebream

- Buildbots: http://buildbot.afpy.org/bluebream/ http://bluebream.buildbot.securactive.org/



What's the deal with the ``/@@`` syntax ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``@@`` is a shortcut for ``++view++``.  (Mnemonically, it kinda looks like a
pair of goggle-eyes)

To specify that you want to traverse to a view named ``bar`` of content
object ``foo``, you could (compactly) say ``.../foo/@@bar`` instead of
``.../foo/++view++bar``.

Note that even the ``@@`` is not necessary if container ``foo`` has no
element named ``bar`` - it only serves to disambiguate between views of an
object and things contained within the object.

``@@`` is also used for static resources. To access the registered static
resource named ``logo.png``, you can use ``/@@/logo.png`` or the equivalent
``/++resource++logo.png``. The ``logo.png`` is a registration name for a
file which may eventually have another filename.

The same applies for a resource directory named ``images``:
``/@@/images/logo.png`` is equivalent to
``/++resource++images/logo.png``. In that case, ``logo.png`` is the real
filename located in the registered resource directory.

.. _faq-security:

Security
--------

How do I configure several classes with the same permissions?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2007-June/006291.html

Use `like_class` attribute of `require` tag, Here are some examples::

  <class class=".MyImage">
    <implements interface=".interfaces.IGalleryItemContained" />
    <require like_class="zope.app.file.interfaces.IImage />
  </class>

  <class class=".MySite">
    <require like_class="zope.app.folder.Folder" />
  </class>


How can I determine (in code) if a principal has the right permissions ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-August/004201.html

The question is: how do I know if the current principal has permission for a
specific view? Something like::

  def canEdit(self):
      ppal = self.request.principal
      return canView('edit', INewsItem, ppal)

Use zope.security.canAccess and/or zope.security.canWrite

To check for a specific permission on an object, you can do something like::

   from zope.security.management import checkPermission
   has_permission = checkPermission('zope.ModifyContent', self.context)


I've registered a PAU in the site-root; now I cannot log in as zope.Manager. What gives?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start debug shell then unregister the utility.  This will then let you log
in as a user defined in ``securitypolicy.zcml``.

Example::

  $ ./bin/paster shell debug.ini
  ...
  >>> import transaction
  >>> from zope.component import getSiteManager
  >>> from zope.app.security.interfaces import IAuthentication
  >>> lsm = getSiteManager(root)
  >>> lsm.unregisterUtility(lsm.getUtility(IAuthentication), IAuthentication)
  >>> transaction.commit()

When you exit debug and start the server, you should be able to log in again
using the user defined in principals.zcml.  This should have the
``zope.Manager`` permission.

To avoid this happening, either assign a role to a user defined in the PAU
or set up a folder beneath the root, make it a site and add and register the
PAU there.  Then you will still be able to log in to the root of the site
and have full permissions.

How do I setup authentication (using a PAU)?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Call this function to setup a site manager with PAU ::

  def setup_site_manager(context):
      context.setSiteManager(LocalSiteManager(context))
      sm = context.getSiteManager()
      pau = PluggableAuthentication(prefix='hello.pau.')
      notify(ObjectCreatedEvent(pau))
      sm[u'authentication'] = pau
      sm.registerUtility(pau, IAuthentication)

      annotation_utility = PrincipalAnnotationUtility()
      sm.registerUtility(annotation_utility, IPrincipalAnnotationUtility)
      session_data = PersistentSessionDataContainer()
      sm.registerUtility(session_data, ISessionDataContainer)

      client_id_manager = CookieClientIdManager()
      notify(ObjectCreatedEvent(client_id_manager))
      sm[u'CookieClientIdManager'] = client_id_manager
      sm.registerUtility(client_id_manager, ICookieClientIdManager)

      principals = PrincipalFolder(prefix='pf.')
      notify(ObjectCreatedEvent(principals))
      pau[u'pf'] = principals
      pau.authenticatorPlugins += (u"pf", )
      notify(ObjectModifiedEvent(pau))

      pau.credentialsPlugins += (u'Session Credentials',)

      p1 = InternalPrincipal('admin1', 'admin1', "Admin 1",
                             passwordManagerName="Plain Text")
      principals['p1'] = p1

      role_manager = IPrincipalRoleManager(context)
      login_name = principals.getIdByLogin(p1.login)
      pid = unicode('hello.pau.' + login_name)
      role_manager.assignRoleToPrincipal('zope.Manager', pid)

How do I logout from BlueBream ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FIXME: Is this valid ?

Logout is available from Zope 3.3 onwards, but it is disabled by
default.  To enable add this line to: ``etc/site.zcml``::

  <adapter factory="zope.app.security.LogoutSupported" />

Why I am getting ILoginPassword adaptation error when accessing login.html ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: https://mail.zope.org/pipermail/zope3-users/2010-January/008745.html

:Q: I am getting an error like this when accessing ``login.html`` view.

::

  .../eggs/zope.principalregistry-3.7.0-py2.5.egg/zope/principalregistry/principalregistry.py",
  line 82, in unauthorized
     a = ILoginPassword(request)
  TypeError: ('Could not adapt', <zope.publisher.browser.BrowserRequest
  instance URL=http://localhost:9060/@@login.html>, <InterfaceClass
  zope.authentication.interfaces.ILoginPassword>)

You need to include ``zope.login`` package in your ZCML configuration file
(``site.zcml``) as the adapter registration is available there::

   <include package="zope.login" />

.. _faq-ui:

User Interface
--------------


How to set default skin ?
~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``browser:defaultSkin`` directive::

  <browser:defaultSkin name="skinname" />

For more details about skinning, read the third part of :ref:`tutorial
<tut3-tutorial>` and :ref:`man-skinning` documentation.

.. _faq-programming:

Programming
-----------

Is API documentation available online?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The BlueBream documentation infrastructure is powerful in that the html
content is generated on the fly.  This makes it somewhat slow while browsing
on older machines.

A cached (and therefore fast) version of the docs are available online at:
http://apidoc.zope.org/++apidoc++/


How do I check out a project/package from Zope subversion repository?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please look at: http://docs.zope.org/developer/noncommitter-svn.html

How do I upgrade from one minor release to another?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the ``bluebream.cfg`` and point the URL of BB version file to new
release and run buildout.  To do this open the ``bluebream.cfg`` file and go
to `[buildout]` part definition (mostly at the beginning).  You can see a
``versions`` option pointing to a URL.  Change the URL to point to the new
release.

Must I always restart the BlueBream server, when I modify my code ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No, you need not to restart, if you use the ``--reload`` option provided by
the ``paster serve`` command.  So, you can run like this::

  ./bin/paster serve --reload debug.ini

Note: We recommend writing automated tests to see the effect of changes.  In
the beginning, this seems like a huge annoyance - however, getting in the
habit of writing unit and functional tests as you develop code will greatly
alleviate this issue.

How do I automatically create some needed object at application startup?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

http://mail.zope.org/pipermail/zope-dev/2007-December/030562.html

Do it by subscribing to ``IDatabaseOpenedWithRootEvent`` (from
``zope.app.appsetup``)

Example code::

  from zope.app.appsetup.interfaces import IDatabaseOpenedWithRootEvent
  from zope.app.appsetup.bootstrap import getInformationFromEvent
  import transaction

  @adapter(IDatabaseOpenedWithRootEvent)
  def create_my_container(event):
      db, connection, root, root_folder = getInformationFromEvent(event)
      if 'mycontainer' not in root_folder:
          root_folder['mycontainer'] = MyContainer()
      transaction.commit()
      connection.close()

Then register this subscriber in your configure.zcml::

  <subscriber handler="myapp.create_my_container" />

How do I validate two or more fields simultaneously?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Consider a simple example: there is a `person` object.  A person object has
`name`, `email` and `phone` attributes.  How do we implement a validation
rule that says either email or phone have to exist, but not necessarily
both.

First we have to make a callable object - either a simple function or
callable instance of a class::

  >>> def contacts_invariant(obj):
  ...     if not (obj.email or obj.phone):
  ...         raise Exception("At least one contact info is required")

Then, we define the `person` object's interface like this.  Use the
`interface.invariant` function to set the invariant::

  >>> class IPerson(interface.Interface):
  ...
  ...     name = interface.Attribute("Name")
  ...     email = interface.Attribute("Email Address")
  ...     phone = interface.Attribute("Phone Number")
  ...
  ...     interface.invariant(contacts_invariant)

Now use `validateInvariants` method of the interface to validate::

  >>> class Person(object):
  ...     interface.implements(IPerson)
  ...
  ...     name = None
  ...     email = None
  ...     phone = None
  >>> jack = Person()
  >>> jack.email = u"jack@some.address.com"
  >>> IPerson.validateInvariants(jack)
  >>> jill = Person()
  >>> IPerson.validateInvariants(jill)
  Traceback (most recent call last):
  ...
  Exception: At least one contact info is required

How do I get the parent of location?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get the parent of an object use ``zope.traversing.api.getParent(obj)``.
To get a list of the parents above an object use
``zope.traversing.api.getParents(obj)``.

How do I set content type header for a HTTP request?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From IRC (http://zope3.pov.lt/irclogs/%23zope3-dev.2006-06-20.log.html)::

  Is there any way using the ``browser:page`` directive, that I can specify
  that the Type of a page rendered is not "text/html" but rather
  "application/vnd.mozilla.xul+xml"?

Use ``request.response.setHeader('content-type', "application/vnd.mozilla.xul+xml")``

How do I give unique names to objects added to a container?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First::

  from zope.app.container.interfaces import INameChooser

Name will be assigned from `create` or `createAndAdd` methods, here is an
eg::

  def create(self, data):
      mycontainer = MyObject()
      mycontainer.value1 = data['value1']
      anotherobj = AnotherObject()
      anotherobj.anothervalue1 = data['anothervalue1']
      namechooser = INameChooser(mycontainer)
      name = chooser.chooseName('AnotherObj', anotherobj)
      mycontainer[name] = anotherobj
      return mycontainer

How do I add a catalog programmatically?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://zopetic.googlecode.com/svn/trunk/src/browser/collectorform.py

See this eg::

  from zopetic.interfaces import ITicket
  from zopetic.interfaces import ICollector
  from zopetic.ticketcollector import Collector
  from zope.app.intid.interfaces import IIntIds
  from zope.app.intid import IntIds
  from zope.component import getSiteManager
  from zope.app.catalog.interfaces import ICatalog
  from zope.app.catalog.catalog import Catalog
  from zope.security.proxy import removeSecurityProxy
  from zope.app.catalog.text import TextIndex

  ...

      def create(self, data):
          collector = Collector()
          collector.description = data['description']
          return collector

      def add(self, object):
          ob = self.context.add(object)
          sm = getSiteManager(ob)
          rootfolder = ob.__parent__
          cat = Catalog()
          rootfolder['cat'] = cat
          if sm.queryUtility(IIntIds) is None:
              uid = IntIds()
              rootfolder['uid'] = uid
              sm.registerUtility(removeSecurityProxy(uid), IIntIds, '')
              pass
          sm.registerUtility(removeSecurityProxy(cat), ICatalog, 'cat')
          cat['description'] = TextIndex('description', ITicket)
          self._finished_add = True
          return ob


Is there a function with which I can get the url of a zope object?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://zope3.pov.lt/irclogs/%23zope3-dev.2006-09-25.log.html

Use::

  zope.component.getMultiAdapter((the_object, the_request),
                                  name='absolute_url')

or::

  zope.traversing.browser.absoluteURL

How do I sort BTreeContainer objects ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Q: Is there a way to sort the objects returned by values() from a
    zope.app.container.btree.BTreeContainer instance?

Ref: http://zope3.pov.lt/irclogs/%23zope3-dev.2006-09-25.log.html

Use ``sorted`` builtin function (available from Python 2.4 onwards) ::

  sorted(my_btree.values())

How do I extract request parameters in a view method?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-July/003876.html

::

  class MyPageView(BrowserView):

     def __call__(self):
        if 'myOperation' in self.request.form:
           param1 = self.request.form['param1']
           param2 = self.request.form['param2']
           do_something(param1, param2)

MyPageView has to be either the default view associated to the 'mypage'
object or a view called 'mypage' associated to the RootFolder object.

Alternately, you could use::

  class MyPageView(BrowserView):

     def __call__(self, param1, param2="DEFAULT"):
        if 'myOperation' in self.request.form:
           do_something(param1, param2)

How do I use Reportlab threadsafely?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-September/004583.html

Use a mutex (a recursive lock makes things easier too)::

  lock = threading.RLock()
  lock.acquire()
  try:
     ...
  finally:
     lock.release()


Why isn't my object getting added to the catalog?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-May/003392.html

Is it adaptable to ``IKeyReference`` ?  If you're using the ZODB, deriving
from ``Persistent`` is enough.


How do I add custom interfaces to pre-existing components/classes?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-November/004918.html

You can do so with a little zcml::

    <class class="zope.app.file.Image">
        <implements interface="mypkg.interfaces.IBloggable" />
    </class>

How do I get IRequest object in event handler ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Q: How I can get IRequest in my event handler (I have only context)?

Ref: http://mail.zope.org/pipermail/zope3-users/2007-April/006051.html

::

  import zope.security.management
  import zope.security.interfaces
  import zope.publisher.interfaces


  def getRequest():
      i = zope.security.management.getInteraction() # raises NoInteraction

      for p in i.participations:
          if zope.publisher.interfaces.IRequest.providedBy(p):
              return p

      raise RuntimeError('Could not find current request.')


How do I create RSS feeds?
~~~~~~~~~~~~~~~~~~~~~~~~~~

Refer http://kpug.zwiki.org/ZopeCreatingRSS (Taken from old zope-cookbook.org)


Where to get zope.conf syntax details ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Refer: http://zope3.pov.lt/irclogs/%23zope3-dev.2008-04-01.log.html

Look at schema.xml inside zope.app.appsetup egg And this xml file can point
you to rest of the syntax.  For details about <zodb> look for component.xml
in ZODB egg

How do I register a browser resource in a test?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First create a fileresource factory (or imageresourcefactory, or another
one)::

    from zope.app.publisher.browser.fileresource import FileResourceFactory
    from zope.security.checker import CheckerPublic
    path = 'path/to/file.png'
    registration_name = 'file.png'
    factory = FileResourceFactory(path, CheckerPublic, name)

Then register it for your layer::

    from zope.component import provideAdapter
    provideAdapter(factory, (IYourLayer,), Interface, name)


How do I get a registered browser resource in a test?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A resource is just an adapter on the request.  It can be seen as a view
without any context.  you can retrieve the FileResource or DirectoryResource
like this:::

  getAdapter(request, name='file.png')

If this is a directory resource, you can access the files in it:::

  getAdapter(request, name='img_dir')['foobar.png']

Then get the content of the file with the GET method (although this is not
part of any interface)::

  getAdapter(request, name='img_dir')['foobar.png'].GET()

How do I write a custom 404 error page?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Register a view for ``zope.publisher.interfaces.INotFound`` in your layer.
The default corresponding view is
``zope.app.exception.browser.notfound.NotFound`` An equivalent exists for
pagelets: ``z3c.layer.pagelet.browser.NotFoundPagelet``

How do I delete an entire tree of objects?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can't control the order of deletion. The problem is that certain objects
get deleted too soon, and other items may need them around, particularly if
you have specified ``IObjectRemoved`` adapters.

You basically have to manually create a deletion dependency tree, and force
the deletion order yourself.  This is one of the problems with events, that
is, their order is not well defined.

.. _faq-configuration:

Configuration and Setup
-----------------------

How do I disable the url selection of the skin?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FIXME: override the  ++skin++ namespace traversal?


How do I set up z3c.traverser and zope.contentprovider?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

z3c.traverser and zope.contentprovider are helpful packages with good and
clear doctests.  It takes not too much time to get up and running with them.
However the packages do not include an example of how to configure your new
useful code into your project.  It is clear from the doctests (and from your
own doctests written while making and testing your own code) **what** needs
to be configured.  But if you are like me and it all isn't yet quite
second-nature, it isn't clear **how** it can be configured.  So, for
z3c.traverser::

  <!-- register traverser for app -->
  <view
    for=".IMallApplication"
    type="zope.publisher.interfaces.browser.IBrowserRequest"
    provides="zope.publisher.interfaces.browser.IBrowserPublisher"
    factory="z3c.traverser.browser.PluggableBrowserTraverser"
    permission="zope.Public"
    />

  <!-- register traverser plugins -->
  <!-- my own plugin -->
  <subscriber
    for=".IMallApplication
         zope.publisher.interfaces.browser.IBrowserRequest"
    provides="z3c.traverser.interfaces.ITraverserPlugin"
    factory=".traverser.MallTraverserPlugin"
  />
  <!-- and traverser package container traverser -->
  <subscriber
    for=".IMallApplication
         zope.publisher.interfaces.browser.IBrowserRequest"
    provides="z3c.traverser.interfaces.ITraverserPlugin"
    factory="z3c.traverser.traverser.ContainerTraverserPlugin"
  />

And for zope.contentprovider::

  <!-- register named adapter for menu provider -->
  <adapter
    provides="zope.contentprovider.interfaces.IContentProvider"
    factory="tfws.menu.provider.MenuProvider"
    name="tfws.menu"
    />

  <!-- this does the directlyProvides -->
  <interface
    interface="tfws.menu.provider.IMenu"
    type="zope.contentprovider.interfaces.ITALNamespaceData"
    />


How do I declare global constants in ZCML?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-September/004381.html

You could just use the ``<utility>`` directive, and group your constants into
logical chunks.

interfaces.py::

  class IDatabaseLoginOptions(Interface):
       username = Attribute()
       password = Attribute()

config.py::

  class DatabaseLoginOptions(object):
       implements(IDatabaseLoginOptions)
       username = 'foo'
       password = 'bar'

configure.zcml::

  <utility factory=".config.DatabaseLoginOptions" />

used::

  opts = getUtility(IDatabaseLoginOptions)

Obviously, this is a bit more work than just declaring some constants in
ZCML, but global constants suffer the same problems whether they're defined
in Python or XML.  Parts of your application are making assumptions that
they are there, with very specific names, which are not type checked.

How can I register a content provider without using viewlet managers?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to create and register simple adapter for object, request
and view that implements the IContentProvider interface::

  class LatestNews(object):

      implements(IContentProvider)
      adapts(Interface, IDefaultBrowserLayer, Interface)

      def __init__(self, context, request, view):
          self.context = context
          self.request = request
          self.__parent__ = view

      def update(self):
          pass

      def render(self):
          return 'Latest news'

In the ZCML::

  <adapter name="latestNews"
           for="* zope.publisher.interfaces.browser.IDefaultBrowserLayer *"
           provides="zope.contentprovider.interfaces.IContentProvider"
           factory=".LatestNews" />

Then you can use it in your TAL templates just like this::

  <div tal:content="provider latestNews" />

Also, you may want to pass some parameters via TAL.  For info on how to do
this, read documentation in the zope.contentprovider.  If you want to bind
some content provider to some skin, change IDefaultBrowserLayer to your skin
interface.


How do I serve out static content in zope3?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://zope3.pov.lt/irclogs/%23zope3-dev.2006-10-02.log.html

See the ZCML directives ``<resource>`` and ``<resourceDirectory>`` they let
you publish static files through BlueBream.  :ref:`More
info. <man-browser-resource>`


Is webdav source server available in BlueBream ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-September/004648.html

Yes, see this: http://svn.zope.org/zope.webdav/trunk

How does one use ZCML overrides in buildout in site.zcml for zc.zope3recipes:app recipe ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2007-April/006106.html

::

  <includeOverrides package="myapp" file="overrides.zcml" />

How write custom traversal in BlueBream ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See this blog entry by Marius Gedminas :
http://mg.pov.lt/blog/zope3-custom-traversal.html

How do I make my project (or a third party project) appear in the APIDOC?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add the following in your apidoc.zcml or configure.zcml:

  <apidoc:rootModule module="myproject" />

If it does not show up, add the following:

  <apidoc:moduleImport allow="true" />

How can I determine (in code) if the instance is running in devmode or not?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 from zope.app.appsetup.appsetup import getConfigContext

    def is_devmode_enabled():
        """Is devmode enabled in zope.conf?"""
        config_context = getConfigContext()
        return config_context.hasFeature('devmode')

.. _faq-misc:

Miscellaneous
-------------

How to check an object is implementing/providing a particular interface ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``providedBy`` available for the interface, it will return True, if
the object provides the interface otherwise False.

Eg::

  >>> IMyInterface.providedBy(myobject)
  True

How do I run a particular test from a package?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ ./bin/test -vpu --dir package/tests test_this_module

Replace 'package' with your package name.

How do I record a session?
~~~~~~~~~~~~~~~~~~~~~~~~~~

You will need to download Shane Hathaways' excellent (and minimal) tcpwatch
package.  This will log ALL data flowing between client and server for you,
and you can use this in developing tests.

To record a session::

  $ mkdir record
  $ tcpwatch.py -L8081:8080 -r record
  # Note: use the "-s" option if you don't need a GUI (Tk).

How do I test file upload using zope.testbrowser?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-July/003830.html

eg:-

::

  >>> import StringIO
  >>> myPhoto = StringIO.StringIO('my photo')
  >>> control = user.getControl(name='photoForm.photo')
  >>> fileControl = control.mech_control
  >>> fileControl.add_file(myPhoto, filename='myPhoto.gif')
  >>> user.getControl(name='photoForm.actions.add').click()
  >>> imgTag =
  'src="http://localhost/++skin++Application/000001/0001/1/photo"'
  >>> imgTag in user.contents
  True


Why do I see ForbiddenAttribute exceptions/errors ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-August/004027.html

ForbiddenAttribute are always (ALWAYS!!!) an sign of missing security
declarations, or of code accessing stuff it shouldn't.  If you're accessing
a known method, you're most definitely lacking a security declaration for
it.

Zope, by default, is set to deny access for attributes and methods that
don't have explicit declarations.

"order" attribute not in browser:menuItem directive:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Q. I want to add a new view tab in the ZMI to be able to edit object
  attributes of some objects.  So I'm adding a new menuItem in the zmi_views
  menu via ZCML with::

    <browser:menuItem
        action="properties.html"
        for=".mymodule.IMyClass"
        title="properties"
        menu="zmi_views"
        permission="zope.ManageContent"
        order="2" />

  (MyClass is just a derived Folder with custom attributes) The problem is:
  the new tab always appear in the first place.  I would like to put it just
  after the "content" tab, not before.  The "order" directive does not work
  for that.  How can I reorder the tabs so that my new tab appears in the
  2nd position?

The default implementation of menus sorts by interface first, and this item
is most specific.  See zope.app.publisher.browser.menu.  If you do not like
this behavior, you have to implement your own menu code.

When running, why ``zlib`` import error appears?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you compile Python, make sure you have installed zlib development
library.

I get a Server Error page when doing something that should work. How do I debug this?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's a nicely formatted IRC log detailing how Steve Alexander found
a particular bug; it gives lots of good advice on tracking bugs:

http://dev.zope.org/Members/spascoe/HowOneZope3BugWasFixed (Scott Pascoe)

Ken Manheimer wrote up an in-depth account of interactive Zope
debugging using the python prompt - it was written for Zope 2, but
many of the principles and some of the actual techniques should
translate to BlueBream.  It's at:

http://www.zope.org/Members/klm/ZopeDebugging

Here is 'Using the Zope Debugger' from the Zope3 docs:

http://svn.zope.org/\*checkout\*/Zope3/trunk/doc/DEBUG.txt

I cannot see source when debugging eggified code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you try to step into eggified code (libraries), you find that the
source file referenced is invalid.  Closer inspection reveals that the
source path referenced has an invalid member like 'tmpXXXXX'.

The fix is easy, but first the reason why this happens:

When you install eggs with easy_install, it creates a temp directory, and
byte compiles the python code.  Hence, the .pyc files that are generated
reference this (working, but temporary) path.  Easy_install then copies the
entire package into the right place, and so the .pyc files are stuck with
invalid references to source files.

To solve this, simply remove all the ".pyc" files from any .egg paths that
you have. On Unix, something like::

 find . -name "*.pyc" | xargs rm

should do the trick.

How can I get a postmortem debugger prompt when a request raises an exception?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Edit the ``debug.ini`` file and update ``[filter-app:main]`` section as
mentioned in the comment there::

  [filter-app:main]
  # Change the last part from 'ajax' to 'pdb' for a post-mortem debugger
  # on the console:
  use = egg:z3c.evalexception#ajax
  next = zope

Restart the server in the foreground (you need an attached console to
interact with the debugger).::

    $ ./bin/paster serve debug.ini

Now, when a request raises an exception, you'll be dropped into a
post-mortem debugger at the point of the exception.

How do I use ZODB blob ?
~~~~~~~~~~~~~~~~~~~~~~~~

You can use `z3c.blobfile <http://pypi.python.org/pypi/z3c.blobfile>`_
implementation for storing images and other normal files.

In BlueBream, blob storage is configured by default.  The Zope configuration
is inside ``etc/zope.conf``::

  <zodb>

    <filestorage>
      path var/filestorage/Data.fs
      blob-dir var/blob
    </filestorage>
  ...


The ``blob-dir`` specifies the directory where you want to store blobs.

How to clear history (pack) in ZODB ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From the debug shell, call the ``app.db.pack`` function::

  $ ./bin/paster shell debug.ini
  >>> app.db.pack()

Do you have an example of CRUD (create/read/update/delete) ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-September/004248.html

The Zope Object DataBase (ZODB), available by default to your application,
makes CRUD very simpe.

Create::

  >>> from recipe import MyFolder, Recipe
  >>> folder = MyFolder()
  >>> recipe = Recipe()
  >>> folder['dead_chicken'] = recipe

Read::

  >>> folder['dead_chicken']
  <worldcookery.recipe.Recipe object at XXX>

Update::

  >>> recipe = folder['dead_chicken']
  >>> recipe.title = u'Dead chicken'
  >>> recipe.description = u'Beat it to death'

Delete::

  >>> del recipe['dead_chicken']

Is there any tool to monitor ZODB activity ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are some packages under development:

- http://pypi.python.org/pypi/zc.z3monitor
- http://pypi.python.org/pypi/zc.zodbactivitylog

Is there any workflow packages available ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Look at these packages:

- http://pypi.python.org/pypi/hurry.workflow
- http://pypi.python.org/pypi/zope.wfmc


.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
