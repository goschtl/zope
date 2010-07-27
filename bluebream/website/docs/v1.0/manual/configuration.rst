.. _man-configuration:

Configuration
*************

Introduction
------------

Developing components alone does not make a framework.  There must be
some configuration utility that tells the system how the components
work together to create the application server framework.  This is
done using the Zope Configuration Markup Language (ZCML) for all
filesystem-based code.  Therefore it is very important that a
developer knows how to use ZCML to hook up his/her components to the
framework.

As stated above, it became necessary to develop a method to setup and
configure the components that make up the application server.  While
it might seem otherwise, it is not that easy to develop an effective
configuration system, since there are several requirements that must
be satisfied.  Over time the following high-level requirements
developed that caused revisions of the implementation and coding
styles to be created:

1. While the developer is certainly the one that writes the initial
   cut of the configuration, this user is not the real target
   audience.  Once the product is written, you would expect a system
   administrator to interact much more frequently with the
   configuration, adding and removing functionality or adjust the
   configuration of the server setup.  System administrators are
   often not developers, so that it would be unfortunate to write the
   configuration in the programming language, here Python.  But an
   administrator is familiar with configuration scripts, shell code
   and XML to some extend.  Therefore an easy to read syntax that is
   similar to other configuration files is of advantage.

2. Since the configuration is not written in Python, it is very
   important that the tight integration with Python is given.  For
   example, it must be very simple to refer to the components in the
   Python modules and to internationalize any human-readable strings.

3. The configuration mechanism should be declarative and not provide
   any facilities for logical operations.  If the configuration would
   support logic, it would become very hard to read and the initial
   state of the entire system would be unclear.  This is another
   reason Python was not suited for this task.

4. Developing new components sometimes requires to extend the
   configuration mechanism.  So it must be easy for the developer to
   extend the configuration mechanism without much hassle.


To satisfy the first requirement, we decided to use an XML-based
language (as the name already suggests).  The advantage of XML is
also that it is a "standard format", which increases the likelihood
for people to be able to read it right away.  Furthermore, we can use
standard Python modules to parse the format and XML namespaces help
us to group the configuration by functionality.

A single configuration step is called a directive.  Each directive is
an XML tag, and therefore the tags are grouped by namespaces.
Directives are done either by simple or complex directives.  Complex
directives can contain other sub-directives.  They are usually used
to provide a set of common properties, but do not generate an action
immediately.

A typical configuration file would be::

  <configure
      xmlns="http://namespaces.zope.org/zope">

    <adapter
        factory="product.FromIXToIY"
        for="product.interfaces.IX"
        provides="product.interfaces.IY" />

  </configure>

All configuration files are wrapped by the configure tag, which
represents the beginning of the configuration.  In the opening of
this tag, we always list the namespaces we wish to use in this
configuration file.  Here we only want to use the generic BlueBream
namespace, which is used as the default.  Then we register an adapter
with the system on line 4-7.  The interfaces and classes are referred
to by a proper Python dotted name.  The configure tag might also
contain an ``i18n_domain`` attribute that contains the domain that is
used for all the translatable strings in the configuration.

As everywhere in BlueBream, there are several naming and coding
conventions for ZCML inside a package.  By default you should name
the configuration file, ``configure.zcml``.  Inside the file you
should only declare namespaces that you are actually going to use.
When writing the directives make sure to logically group directives
together and use comments as necessary.  Comments are written using
the common XML syntax: ``<!--...-->``.  For more info see Steve's
detailed ZCML Style Guide at
http://wiki.zope.org/zope3/ZCMLStyleGuide for more info.

To satisfy our fourth requirement, it is possible to easily extend
ZCML through itself using the meta namespace.  A directive can be
completely described by four components, its name, the namespace it
belongs to, the schema and the directive handler::

  <meta:directive
      namespace="http://namespaces.zope.org/zope"
      name="adapter"
      schema=".metadirectives.IAdapterDirective"
      handler=".metaconfigure.adapterDirective" 
      />

These meta-directives are commonly placed in a file called
``meta.zcml``.

The schema of a directive, which commonly lives in a file called
``metadirectives.py``, is a simple BlueBream schema whose fields
describe the available attributes for the directive.  The
configuration system uses the fields to convert and validate the
values of the configuration for use.  For example, dotted names are
automatically converted to Python objects.  There are several
specialized fields specifically for the configuration machinery:

- ``PythonIndentifier`` - This field describes a python identifier,
  for example a simple variable name.

- ``GlobalObject`` - An object that can be accessed as a module
  global, such as a class, function or constant.

- ``Tokens`` - A sequence that can be read from a space-separated
  string.  The value_type of the field describes token type.

- ``Path`` - A file path name, which may be input as a relative path.
  Input paths are converted to absolute paths and normalized.

- ``Bool`` - An extended boolean value.  Values may be input (in
  upper or lower case) as any of: yes, no, y, n, true, false, t, or
  f.

- ``MessageID`` - Text string that should be translated.  Therefore
  the directive schema is the only place that needs to deal with
  internationalization.  This satisfies part of requirement 2 above.

The handler, which commonly lives in a file called
``metaconfigure.py``, is a function or another callable object that
knows what needs to be done with the given information of the
directive.  Here is a simple (simplified to the actual code)
example::


  def adapter(_context, factory, provides, for_, name=''):

      _context.action(
          discriminator = ('adapter', for_, provides, name),
          callable = provideAdapter,
          args = (for_, provides, factory, name),
          )

The first argument of the handler is always the _context variable,
which has a similar function to self in classes.  It provides some
common methods necessary for handling directives.  The following
arguments are the attributes of the directive (and their names must
match).  If an attribute name equals a Python keyword, like for in
the example, then an underscore is appended to the attribute name.

The handler should also not directly execute an action, since the
system should first go through all the configuration and detect
possible conflicts and overrides.  Therefore the ``_context`` object
has a method called action that registers an action to be executed at
the end of the configuration process.  The first argument is the
discriminator, which uniquely defines a specific directive.  The
callable is the function that is executed to provoke the action, the
``args`` argument is a list of arguments that is passed to the
callable and the kw contains the callable's keywords.

As you can see, there is nothing inheritly difficult about ZCML.
Still, people coming to BlueBream often experience ZCML as the most
difficult part to understand.  This often created huge discussions
about the format of ZCML.  However, we believe that the problem lies
not within ZCML itself, but the task it tries to accomplish.  The
components themselves always seem so clean in implementation; and
then you get to the configuration.  There you have to register this
adapter and that view, make security assertions, and so on.  And this
in itself seems overwhelming at first sight.  When I look at a
configuration file after a long time I often have this feeling too,
but reading directive for directive often helps me to get a quick
overview of the functionality of the package.  In fact, the
configuration files can help you understand the processes of the
BlueBream framework without reading the code, since all of the
interesting interactions are defined right there.

Furthermore, ZCML is well documented at many places, including the
BlueBream API documentation tool at
http://apidoc.zope.org/++apidoc++/ .  Here is a short list of the
most important namespaces:

- ``zope`` - This is the most generic and fundamental namespace of all,
  since it allows you to register all basic components with the
  component architecture.

- ``browser`` - This namespace contains all of the directives that deal with
  HTML output, including managing skins and layer, declare new views
  (pages) and resources as well as setup auto-generated forms.

- ``meta`` - As discussed above, you can use this namespace to extend
  available directives.

- ``xmlrpc`` - This is the equivalent to browser, except that allows
  one to specify methods of components that should be available via
  XML-RPC.

- ``i18n`` - This namespace contains all internationalization- and
  localization-specific configuration. Using registerTranslations you
  can register new message catalogs with a translation domain.

- ``help`` - Using the register directive, you can register new help
  pages with the help system. This will give you context-sensitive
  help for the ZMI screens of your products.

- ``mail`` - Using the directives of this namespace you can setup mailing
  components that your application can use to

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
