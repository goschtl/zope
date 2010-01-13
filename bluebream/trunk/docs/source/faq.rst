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
framework written in the Python programming language.  BlueBream provides
a component architecture, transactional object database, tightly
integrated security model and many other features.

BlueBream is coming from the Zope community which is started around 1998.
Initially Zope's core technologies were designed by Zope Corporation.
The development of BlueBream started in late 2001.  In November 2004,
BlueBream was released.  BlueBream is a complete rewrite that only preserves
the original ZODB object database.  The design of BlueBream is driven by
the needs of large companies.  It is directly intended for enterprise
web application development using the newest development paradigms.
Extreme programming development process has a real influence in BlueBream
development.  Automated testing is a major strength of BlueBream.
Sprints_ were introduced to help accelerate BlueBream development.  In
2006 `Zope foundation`_ was formed to help organize and formalize the
relationships with the Zope community.

.. _Sprints: http://www.zopemag.com/Guides/miniGuide_ZopeSprinting.html
.. _Zope foundation: http://www.zope.org/foundation
.. _subversion: http://svn.zope.org/

Why BlueBream ?
~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-August/004205.html

BlueBream has:

  - WSGI-compatible object publisher (zope.publisher)

  - Object database (ZODB) for transparently persisting objects; comes
    with load-balancing support (ZEO).

  - Component Architecture for making things pluggable very easily
    (zope.component)

  - XML-configuration language for registering components
    (zope.configuration), not mandatory but pretty much standard

  - Flexible security architecture with pluggable security policies
    (zope.security)

  - Good unit, integration and functional testing frameworks
    (zope.testing, zope.testbrowser)

  - XHTML-compliant templating language (zope.pagetemplate)

  - Schema engine and automatic form generation machinery
    (zope.formlib)

  - many more core and third-party packages that may already solve
    some of your problems. See http://svn.zope.org, for instance.

BlueBream is:

  - ZPL (BSD-ish license)

  - Owned by Zope Foundation

  - written mostly by contributors, not just Zope Corporation.

  - usable in pieces or in whole

What is the Zope Foundation ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From http://foundation.zope.org::

  The Zope Foundation has the goal to promote, maintain, and develop
  the Zope platform.  It does this by supporting the Zope community.
  Our community includes the open source community of contributors to
  the Zope software, contributors to the documentation and web
  infrastructure, as well as the community of businesses and
  organizations that use Zope.

  The Zope Foundation is the copyright holder of the Zope software
  and many extensions and associated software.  The Zope Foundation
  also manages the zope.org website, and manages the infrastructure
  for open source collaboration.

For more details: http://foundation.zope.org/about


How can I help ?
~~~~~~~~~~~~~~~~

If you're interested in helping and you have time, educate yourself
on the component architecture and BlueBream then volunteer to assist
in your particular area of expertise.  Please come to our IRC
channel: #bluebream at irc.freenode.net


What is the license of BlueBream ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BlueBream is licensed under Zope Public License, Version 2.1 (ZPL).

Is BlueBream stable enough to be used in production environment ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, it is stable enough to be used in production environment.
BlueBream (or old Zope 3) is used in several larger production sites
already.  Several custom solutions have been written too.  But the
development of BlueBream will probably never be done, it will
continue until all our needs are met :)

Which Python version is required?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python 2.6 will the supported version for BlueBream 1.0 final
release.


What is the KGS (Known Good Set) ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting from version 3.4, Zope has been split into many packages
called "eggs", that are released independently.  The KGS is a set of
python eggs, that are known to work together, and that are listed in
a separate Python Package Index (to be used with
setuptools/easy_install and zc.buildout).

* The KGS package index for zope 3.4 is : http://download.zope.org/zope3.4/
* Some explanations about using the KGS : http://download.zope.org/zope3.4/intro.html

The KGS is used to define what a major release of Zope is.  The KGS
for Zope 3.4 is here: http://svn.zope.org/zope.release/tags/

The generic code that is used to build and maintain any KGS is here:
http://svn.zope.org/zope.kgs/

How do I start a new BlueBream project ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can start with the :ref:`started-getting` documentation.

.. _faq-concepts:

Concepts
--------

What is the component architecture ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's similar to other component architectures in that it lets you fit
small pieces of functionality together.  While Zope 2 has many parts
welded together with inheritance, BlueBream will let you take things
apart and put them together like LEGO bricks(TM).

Where can I find pointers to resources ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. IRC : #zope3-dev at irc.freenode.net , logs at : http://zope3.pov.lt/irclogs

2. Users list (for development with BlueBream): zope3-users@zope.org,
   archives at : http://mail.zope.org/pipermail/zope3-users/

3. Developers list (for development of BlueBream itself) :
   zope-dev@zope.org, archives at :
   http://mail.zope.org/pipermail/zope-dev/

4. Zope 3 book by Philipp von Weitershausen :
   http://worldcookery.com/

5. Planet :  http://planetzope.org/

6. https://wiki.ubuntu.com/LearningZope3


What's the deal with the ``/@@`` syntax ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``@@`` is a shortcut for ``++view++``.  (Mnemonically, it kinda looks
like a pair of goggle-eyes)

To specify that you want to traverse to a view named ``bar`` of
content object ``foo``, you could (compactly) say ``.../foo/@@bar``
instead of ``.../foo/++view++bar``.

Note that even the ``@@`` is not necessary if container ``foo`` has
no element named ``bar`` - it only serves to disambiguate between
views of an object and things contained within the object.

Are ContainerTypesConstraint & ItemTypePrecondition deprecated ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These two are not deprecated, but ``contains`` and ``containers``
functions are recommended.

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

The question is: how do I know if the current principal has permission
for a specific view? Something like::

  def canEdit(self):
      ppal = self.request.principal
      return canView('edit', INewsItem, ppal)

Use zope.security.canAccess and/or zope.security.canWrite

To check for a specific permission on an object, you can do something like::

   from zope.security.management import checkPermission
   has_permission = checkPermission('zope.ModifyContent', self.context)


I've registered a PAU in the site-root; now I cannot log in as zope.Manager. What gives?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start zopedebug then unregister the utility. This will then let you
log in as a user defined in principals.zcml.

Example (execute the following with zopedebug)::

  import transaction
  from zope.component import getSiteManager
  from zope.app.security.interfaces import IAuthentication

  lsm = getSiteManager(root)
  lsm.unregisterUtility(lsm.getUtility(IAuthentication), IAuthentication)

  transaction.commit()

When you exit zopedebug and start the server, you should be able to
log in again using the user defined in principals.zcml.  This should
have the zope.Manager permission.

To avoid this happening, either assign a role to a user defined in the
PAU or set up a folder beneath the root, make it a site and add and
register the PAU there. Then you will still be able to log in to the
root of the site and have full permissions.

How do I setup authentication (using a PAU)?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Via the ZMI:

 * go to the site manager (in the root, or in your folder/site)
 * add a Pluggable Authentication Utility (name as you want, prefix empty)
 * enter it and activate "no challenge if auth" and "session credentials" in this order
 * add a Principal Folder (name and prefix as you want)
 * return back to the PAU, and activate your Principal Folder
 * Now, register both the PAU and the Principal Folder 
 * Then you can add users in your Principal Folder (aka Principals)

Via the API::

  site = getSite()
  sm = site.getSiteManager()
  pau = PluggableAuthentication()
  sm['authentication'] = pau
  sm.registerUtility(pau, IAuthentication)
  users = PrincipalFolder()
  sm['authentication']['Users'] = users
  sm.registerUtility(users, IAuthenticatorPlugin, name="Users")
  pau.authenticatorPlugins = (users.__name__, )
  pau.credentialsPlugins = ( "No Challenge if Authenticated", "Session Credentials" ) 

How do I setup authentication (via ldap)?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install ldapadapter and ldappas.

Via the ZMI:

 * go to the site manager (in the root, or in your folder/site)
 * add a ldapadapter and configure it for your ldapserver, test it
 * Now, register it with some custom name (example, ldapadapter.interfaces.ILDAPAdapter utility named 'myldap')
 * add a Pluggable Authentication Utility (name as you want, prefix empty)
 * enter it and activate "no challenge if auth" and "session credentials" in this order
 * add a LDAP Authentication plugin
 * return back to the PAU, and activate your ldap plugin
 * Now, register both the PAU and the ldap plugin
 * Then you can see your ldap-users in Grant action

How do I logout from BlueBream ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2005-October/001112.html

Ref: http://svn.zope.org/\*checkout\*/Zope3/branches/3.3/src/zope/app/security/browser/loginlogout.txt

Logout is available from Zope 3.3 onwards, but it is disabled by
default.  To enable add this line to
``$instance/etc/overrides.zcml``::

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

You need to inlcude ``zope.login`` package in your ZCML configuration
file (``site.zcml``) as the adapter registration is available there::

   <include package="zope.login" />

.. _faq-ui:

User Interface
--------------

How do I disable the url selection of the skin?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FIXME: override the  ++skin++ namespace traversal?


How do I set up z3c.traverser and zope.contentprovider?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

z3c.traverser and zope.contentprovider are helpful packages with good
and clear doctests. It takes not too much time to get up and running
with them.  However the packages do not include an example of how to
configure your new useful code into your project. It is clear from the
doctests (and from your own doctests writen while making and testing
your own code) **what** needs to be configured. But if you are like me
and it all isn't yet quite second-nature, it isn't clear **how** it
can be configured. So, for z3c.traverser::

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

You could just use the <utility> directive, and group your constants into
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

Obviously, this is a bit more work than just declaring some constants
in ZCML, but global constants suffer the same problems whether they're
defined in Python or XML.  Parts of your application are making
assumptions that they are there, with very specific names, which are
not type checked.

How can I register a content provider without using viewlet managers?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to create and register simple adapter for object, request and view that implements the IContentProvider interface::

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

Also, you may want to pass some parameters via TAL. For info on how to do this, read documentation in the zope.contentprovider. If you want to bind some content provider to some skin, change IDefaultBrowserLayer to your skin interface.

How do I serve out static content in zope3?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://zope3.pov.lt/irclogs/%23zope3-dev.2006-10-02.log.html

See the ZCML directives <resource> and <resourceDirectory> they let
you publish static files through Zope

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

See this blog entry by Marius Gedminas : http://mg.pov.lt/blog/zope3-custom-traversal.html

.. _faq-programming:

Programming
-----------

Is there a tutorial?
~~~~~~~~~~~~~~~~~~~~

 - http://www.benjiyork.com/quick_start/
 - [Zope 3 in 30 Minutes]
 - ProgrammerTutorial (out dated)

Is API documentation available online?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Zope3 documentation infrastructure is powerful in that the html
content is generated on the fly. This makes it somewhat slow while
browsing on older machines.

A cached (and therefore fast) version of the docs are available online at:
http://apidoc.zope.org/++apidoc++/


How do I check out a project/package from Zope subversion repository?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: SettingUpAZope3Sandbox

You can browse available projects here: http://svn.zope.org (in the
package names, "zc" stands for "Zope Corporation", "z3c" stands for
"Zope 3 Community")

Then, to check out Zope3 trunk anonymously::

  svn co svn://svn.zope.org/repos/main/Zope3/trunk Zope3

Stable branches are available from :
http://svn.zope.org/Zope3/branches (online) .  And release tags from:
http://svn.zope.org/Zope3/tags (online)

To check out Zope 3.3 stable branch::

  svn co svn://svn.zope.org/repos/main/Zope3/branches/3.3 Zope33


How do I upgrade from one minor release to another?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-August/004025.html

You can have more than one BlueBream installed, e.g. you can install Zope
3.2.1 in parallel to 3.2.0 and switch your instance over to 3.2.1 (by
editing the start scripts in $INSTANCE/bin). You can also install Zope
3.2.1 into the place where 3.2.0 was installed; your instance should
continue to work. Such a thing isn't recommended when upgrading
between major versions, though (3.2 to 3.3).

Note: this is even easier if you use an egg based infrastructure. However,
learning how to use eggs in a realistic way, is a significant leap.

Must I always restart the  zope server, when I modify my code? 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-September/004531.html

  - Yes, you have to restart the server, though we recommend writing unit
    tests that take a lot less time than starting Zope)

  - This probably isn't going to be implemented (it's very much non-trivial)

  - Significantly, you don't have to restart for changes in resources or Page Templates.

In the beginning, this seems like a huge annoyance - however, getting in the 
habit of writing unit and functional tests as you develop code will greatly 
alleviate this issue.

How do I automatically create some needed object at application startup?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

http://mail.zope.org/pipermail/zope-dev/2007-December/030562.html

Do it by subscribing to IDatabaseOpenedWithRootEvent (from zope.app.appsetup)

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

Consider a simple example: there is a `person` object.  A person
object has `name`, `email` and `phone` attributes.  How do we
implement a validation rule that says either email or phone have to
exist, but not necessarily both.

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
  Exception: At least one contact info is rquired

How do I get the parent of location?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get the parent of an object use
zope.traversing.api.getParent(obj). To get a list of the parents above
an object use zope.traversing.api.getParents(obj).

How do I set content type header for a HTTP request?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From IRC (http://zope3.pov.lt/irclogs/%23zope3-dev.2006-06-20.log.html)::

  Is there any way using the browser:page directive, that I can
  specify that the Type of a page rendered is not "text/html" but
  rather "application/vnd.mozilla.xul+xml"?

Use request.response.setHeader('content-type', ...)


How do I give unique names to objects added to a container?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First::

  from zope.app.container.interfaces import INameChooser

Name will be assigned from 'create' or 'createAndAdd' methods, here is
an eg::

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

see this eg::

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

MyPageView has to be either the default view associated to the 'mypage' object
or a view called 'mypage' associated to the RootFolder object.

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

Is it adaptable to IKeyReference?  If you're using the ZODB, deriving
from Persistent is enough.


How do I add custom interfaces to pre-existing components/classes?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-November/004918.html

You can do so with a little zcml::

    <class class="zope.app.file.Image">
        <implements interface=".interfaces.IBloggable" />
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

Look at schema.xml inside zope.app.appsetup egg
And this xml file can point you to rest of the syntax.
for details about <zodb> look for component.xml in ZOBD egg

How do I register a browser resource in a test?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
First create a fileresource factory (or imageresourcefactory, or another one)::

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

A resource is just an adapter on the request. It can be seen as a view without any context.
you can retrieve the FileResource or DirectoryResource like this:::

    getAdapter(request, name='file.png')

If this is a directory resource, you can access the files in it:::

    getAdapter(request, name='img_dir')['foobar.png']

then get the content of the file with the GET method (although this is not part of any interface)::

    getAdapter(request, name='img_dir')['foobar.png'].GET()

How do I write a custom 404 error page?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Register a view for zope.publisher.interfaces.INotFound in your layer.
The default corresponding view is zope.app.exception.browser.notfound.NotFound
An equivalent exists for pagelets : z3c.layer.pagelet.browser.NotFoundPagelet

How do I delete an entire tree of objects?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can't control the order of deletion. The problem is that
certain objects get deleted too soon, and other items may need
them around, particularly if you have specified IObjectRemoved
adapters.

You basically have to manually create a deletion dependency tree,
and force the deletion order yourself.  This is one of the
problems with events, ie: their order is not well defined.

.. _faq-configuration:

Configuration and Setup
-----------------------


How do I disable the url selection of the skin?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FIXME: override the  ++skin++ namespace traversal?


How do I set up z3c.traverser and zope.contentprovider?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

z3c.traverser and zope.contentprovider are helpful packages with good
and clear doctests. It takes not too much time to get up and running
with them.  However the packages do not include an example of how to
configure your new useful code into your project. It is clear from the
doctests (and from your own doctests writen while making and testing
your own code) **what** needs to be configured. But if you are like me
and it all isn't yet quite second-nature, it isn't clear **how** it
can be configured. So, for z3c.traverser::

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

You could just use the <utility> directive, and group your constants into
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

Obviously, this is a bit more work than just declaring some constants
in ZCML, but global constants suffer the same problems whether they're
defined in Python or XML.  Parts of your application are making
assumptions that they are there, with very specific names, which are
not type checked.

How can I register a content provider without using viewlet managers?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to create and register simple adapter for object, request and view that implements the IContentProvider interface::

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

Also, you may want to pass some parameters via TAL. For info on how to do this, read documentation in the zope.contentprovider. If you want to bind some content provider to some skin, change IDefaultBrowserLayer to your skin interface.


How do I serve out static content in zope3?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://zope3.pov.lt/irclogs/%23zope3-dev.2006-10-02.log.html

See the ZCML directives <resource> and <resourceDirectory> they let
you publish static files through Zope


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

See this blog entry by Marius Gedminas : http://mg.pov.lt/blog/zope3-custom-traversal.html

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

How do I run a particular test from a package?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Go to your $ZOPE3INSTANCE/etc, then::

  $ cd $HOME/myzope/etc
  $ ../bin/test.py -vpu --dir package/tests test_this_module

Here I assumed $HOME/myzope is your Zope3 instance directory.  Replace
'package' with your package name.

How do I record a session?
~~~~~~~~~~~~~~~~~~~~~~~~~~

You will need to download Shane Hathaways' excellent (and minimal)
tcpwatch package. This will log ALL data flowing between client
and server for you, and you can use this in developing tests.

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
declarations, or of code accessing stuff it shouldn't. If you're accessing
a known method, you're most definitely lacking a
security declaration for it.

Zope, by default, is set to deny access for attributes and methods that don't
have explicit declarations.

"order" attribute not in browser:menuItem directive:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Q. I want to add a new view tab in the ZMI to be able to edit object
  attributes of some objects. So I'm adding a new menuItem in the
  zmi_views menu via ZCML with::

    <browser:menuItem
        action="properties.html"
        for=".mymodule.IMyClass"
        title="properties"
        menu="zmi_views"
        permission="zope.ManageContent"
        order="2" />

  (MyClass is just a derived Folder with custom attributes) The
  problem is: the new tab always appear in the first place. I would
  like to put it just after the "content" tab, not before. The "order"
  directive does not work for that. How can I reorder the tabs so that
  my new tab appears in the 2nd position?

The default implementation of menus sorts by interface first, and this
item is most specific. See zope.app.publisher.browser.menu. If you do
not like this behavior, you have to implement your own menu code.

utf-8 error in i18nfile
~~~~~~~~~~~~~~~~~~~~~~~

  Q. Why do I always get an error when I try to add some utf-8 text
  into an i18nfile? I just add an i18nfile in the ZMI, then I chose a
  name and I set the contentType to "text/plain;charset=utf-8". If I
  enter some text with accents like "ÃÂ©Ã ÃÂ®ÃÂ®", I get a system error
  which says : UnicodeDecodeError: 'ascii' codec can't decode byte
  0xc3 in position 0: ordinal not in range(128). I don't get any error
  with a simple File object.

Okay, I18n file is a demo that is probably not well-developed. Don't
use it. I will propose to not distribute it anymore. Noone is using
it, so you are on your own finding the problem and providing a patch.

When running $instance/bin/runzope zlib import error appears?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope/2004-November/154739.html

When you compile Python, make sure you have installed zlib development
library.  In Debian 3.1 (Sarge) it is `zlib1g-dev`.

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

When you try to step into eggified code (libraries), you find that the source file
referenced is invalid. Closer inspection reveals that the source path referenced
has an invalid member like 'tmpXXXXX'.

The fix is easy, but first the reason why this happens:

When you install eggs with easy_install, it creates a temp directory,
and byte compiles the python code. Hence, the .pyc files that are generated
reference this (working, but temporary) path. Easy_install then copies the
entire package into the right place, and so the .pyc files are stuck with 
invalid references to source files.

To solve this, simply remove all the ".pyc" files from any .egg paths that you
have. On Unix, something like::

 find . -name "*.pyc" | xargs rm

should do the trick.

How do I get more details about system errors, in the browser itself?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-November/004881.html

Use the Debug skin via ++skin++Debug or via ++debug++errors (the
latter is better if you still want to see your own skin).

How can I get a postmortem debugger prompt when a request raises an exception?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Edit your zope.conf and change the server type from HTTP (or whatever it
is) to PostmortemDebuggingHTTP or WSGI-PostmortemDebuggingHTTP.::

    <server>
      address 8080
      type PostmortemDebuggingHTTP
    </server>

Restart the server in the foreground (you need an attached console to interact
with the debugger).::

    path/to/instance/control/script stop
    path/to/instance/control/script fg

Now, when a request raises an exception, you'll be dropped into a post-mortem
debugger at the point of the exception.

What version of ZODB does BlueBream use ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BlueBream 1.0 is using ZODB 3.9.x

How do I use ZODB blob ?
~~~~~~~~~~~~~~~~~~~~~~~~

You can use `z3c.blobfile
<http://pypi.python.org/pypi/z3c.blobfile>`_ implementation for
storing images and other normal files.

In BlueBream, blob storage is configured by default.  The final
configuration is inside ``etc/zope.conf``, but this configuration
file is generated from a template by Buildout.  The templates is
available in ``templates/zope_conf.in``.  So, if you want to make any
changes, you can do it there::

  <zodb>
    # Wrap standard FileStorage with BlobStorage proxy to get ZODB blobs
    # support.
    # This won't be needed with ZODB 3.9, as its FileStorage supports
    # blobs by itself. If you use ZODB 3.9, remove the proxy and specify
    # the blob-dir parameter right in in filestorage, just after path.
    <blobstorage>
      blob-dir ${config:blob}
      <filestorage>
        path ${config:filestorage}/Data.fs
      </filestorage>
    </blobstorage>
  </zodb>

The ``blob-dir`` specifies where you want to store blobs.  As you can
see, the directory location information is getting from Buildout
configuration file.  So, if you want to change the location, you need
to change it in the Buildout configuration.

Do you have an example of CRUD (create/read/update/delete) ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ref: http://mail.zope.org/pipermail/zope3-users/2006-September/004248.html

The Zope Object DataBase (ZODB), available by default to your application,
makes CRUD very simple.

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

Ref: http://zope3.pov.lt/irclogs/%23zope3-dev.2007-05-15.log.html

There are some packages under development:

- http://svn.zope.org/zc.z3monitor
- http://svn.zope.org/zc.zservertracelog
- http://svn.zope.org/zc.zodbactivitylog

Where is zope.app.workflow ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It has never been released with BlueBream, just as an add-on package.
Please look at these packages:

- http://pypi.python.org/pypi/hurry.workflow

- http://pypi.python.org/pypi/zope.wfmc


.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
