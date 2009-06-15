hurry.custom
============

Introduction
------------

This package contains an infrastructure and API for the customization
of templates. The only template languages supported by this system are
"pure-push" languages which do not call into arbitrary Python code
while executing. Examples of such languages are json-template
(supported out of the box) and XSLT. The advantage of such languages
is that they are reasonably secure to expose through-the-web
customization without an elaborate security infrastructure.

Let's go through the use cases that this system must support:

* templates exist on the filesystem, and those are used by default.

* templates can be customized. 

* this customization can be stored in another database (ZODB,
  filesystem, a relational database, etc); this is up to the person
  integrating ``hurry.custom``.

* update template automatically if it is changed in the database.

* it is possible to retrieve the template source (for display in a UI
  or for later use within for instance a web-browser for client-side
  rendering).

* support server-side rendering of templates (producing HTML or an
  email message or whatever). Input is particular to template language
  (but should be considered immutable).

* provide (static) input samples (such as JSON or XML files) to make
  it easier to edit and test templates. These input samples can be
  added both to the filesystem as well as to the database.

* round-trip support. The customized templates and samples can be
  retrieved from the database and exported back to the
  filesystem. This is useful when templates need to be taken back
  under version control after a period of customization by end users.

The package is agnostic about (these things are pluggable):

* the database used for storing customizations of templates or their
  samples.

* the particular push-only template language used.

What this package does not do is provide a user interface. It only
provides the API that lets you construct such user interfaces.

Creating and registering a template language
--------------------------------------------

In order to register a new push-only template we need to provide a
factory that takes the template text (which could be compiled down
further). Instantiating the factory should result in a callable that
takes the input data (in whatever format is native to the template
language). The ``ITemplate`` interface defines such an object::

  >>> from hurry.custom.interfaces import ITemplate, CompileError, RenderError

For the purposes of demonstrating the functionality in this package,
we supply a very simplistic push-only templating language, based on
template strings as provided by the Python ``string`` module::

  >>> import string
  >>> from zope.interface import implements
  >>> class StringTemplate(object):
  ...    implements(ITemplate)
  ...    def __init__(self, text):
  ...        if '&' in text:
  ...            raise CompileError("& in template!")
  ...        self.source = text
  ...        self.template = string.Template(text)
  ...    def __call__(self, input):
  ...        try:
  ...            return self.template.substitute(input)
  ...        except KeyError, e:
  ...            raise RenderError(unicode(e))

Let's demonstrate it. To render the template, simply call it with the
data as an argument::

  >>> template = StringTemplate('Hello $thing')
  >>> template({'thing': 'world'})
  'Hello world'

Note we have put some special logic in the ``__init__`` that triggers a
``CompileError`` error if the string ``&`` is found in the
template. This is so we can easily demonstrate templates that are
broken - treat a template with ``&`` as a template with a syntax
(compilation) error. Let's try it::

  >>> template = StringTemplate('Hello & bye')
  Traceback (most recent call last):
    ...
  CompileError: & in template!

We have also made sure we catch a possible runtime error (a
``KeyError`` when a key is missing in the input dictionary in this
case) and raise this as a ``RenderError``::

  >>> template = StringTemplate('Hello $thing')
  >>> template({'thang': 'world'})
  Traceback (most recent call last):
    ...
  RenderError: 'thing'

The template class defines a template language. Let's register the
template language so the system is aware of it and treats ``.st`` files
on the filesystem as a string template::

  >>> from hurry import custom
  >>> custom.register_language(StringTemplate, extension='.st')

Loading a template from the filesystem
--------------------------------------

``hurry.custom`` assumes that any templates that can be customized
reside on the filesystem primarily and are shipped along with an
application's source code. They form *collections*. A collection is
simply a directory (with possible sub-directories) that contains
templates.

Let's create a collection of templates on the filesystem::

  >>> import tempfile, os
  >>> templates_path = tempfile.mkdtemp(prefix='hurry.custom')

We create a single template, ``test1.st`` for now::

  >>> test1_path = os.path.join(templates_path, 'test1.st')
  >>> f = open(test1_path, 'w')
  >>> f.write('Hello $thing')
  >>> f.close()

We also create an extra template::

  >>> test2_path = os.path.join(templates_path, 'test2.st')
  >>> f = open(test2_path, 'w')
  >>> f.write("It's full of $thing")
  >>> f.close()

In order for the system to work, we need to register this collection
of templates on the filesystem. We need to supply a globally unique
collection id, the templates path, and (optionally) a title::

  >>> custom.register_collection(id='templates', path=templates_path)

We can now render the template::

  >>> custom.render('templates', 'test1.st', {'thing': 'world'})
  u'Hello world'

We'll try another template::

  >>> custom.render('templates', 'test2.st', {'thing': 'stars'})
  u"It's full of stars"

We can also look up the template object::

  >>> template = custom.lookup('templates', 'test1.st')

We got our proper template::

  >>> template({'thing': 'world'})
  u'Hello world'

The templat also has a ``source`` attribute::

  >>> template.source
  u'Hello $thing'

The source text of the template was interpreted as a UTF-8 string. The
template source should always be in unicode format (or in plain
ASCII).

The underlying template will not be reloaded unless it is changed on
the filesystem::

  >>> orig = template.template

When we trigger a potential reload nothing happens - the template did
not change on the filesystem::

  >>> template.source
  u'Hello $thing'
  >>> template.template is orig
  True
  
It will however automatically reload the template when it has changed
on the filesystem. We will demonstrate that by modifying the file::

  >>> f = open(test1_path, 'w')
  >>> f.write('Bye $thing')
  >>> f.close()

Unfortunately this won't work in the tests as the modification time of
files has a second-granularity on some platforms, way too long to
delay the tests for. We will therefore manually update the last updated
time as a hack::

  >>> template._last_updated -= 1

Now the template will have changed::

  >>> template.source
  u'Bye $thing'
  
  >>> template({'thing': 'world'})
  u'Bye world'

Customization database
----------------------

So far all our work was done in the root (filesystem) database. We can
get it now::

  >>> root_db = custom.root_collection('templates')

Before any customization database was registered we could also have
gotten it using ``custom.collection``, which gets the collection in
context::

  >>> custom.collection('templates') is root_db
  True
 
Let's now register a customization database for our collection, in a
particular site. This means in such a site, the new customized
template database will be used (with a fallback on the original one if
no customization can be found or if there is an error in the use of a
customization).

Let's create a site first::

  >>> site1 = DummySite(id=1)

We register a customization database for our collection named
``templates``. For the purposes of testing we will use an in-memory
database::

  >>> mem_db = custom.InMemoryTemplateDatabase('templates', 'Templates')
  >>> from hurry.custom.interfaces import ITemplateDatabase
  >>> sm1 = site1.getSiteManager()
  >>> sm1.registerUtility(mem_db, provided=ITemplateDatabase, 
  ...   name='templates')

We go into this site::

  >>> setSite(site1)

We can now find this collection using ``custom.collection``::

  >>> custom.collection('templates') is mem_db
  True

The collection below it is the root collection::

  >>> custom.next_collection('templates', mem_db) is root_db
  True

Below this, there is no collection and we'll get a lookup error::

  >>> custom.next_collection('templates', root_db)
  Traceback (most recent call last):
    ...
  ComponentLookupError: No collection available for: templates

We haven't placed any customization in the customization database
yet, so we'll see the same thing as before when we look up the
template::

  >>> custom.render('templates', 'test1.st', {'thing': "universe"})
  u'Bye universe'

Customization of a template
---------------------------

Now that we have a locally set up customization database, we can
customize the ``test1.st`` template. 

In this customization we change 'Bye' to 'Goodbye'::

  >>> source = root_db.get_source('test1.st')
  >>> source = source.replace('Bye', 'Goodbye')

We now need to update the database so that it has this customized
version of the template. We do this by calling the ``update`` method
on the database with the template id and the new source.

This update operation is not supported on the default filesystem
database::

   >>> root_db.update('test1.st', source)
   Traceback (most recent call last):
     ...
   NotSupported: Cannot update templates in FilesystemTemplateDatabase.

It is supported on the site-local in-memory database we've just
installed though::

  >>> mem_db.update('test1.st', source)

All you need to do to hook in your own database is to implement the
``ITemplateDatabase`` interface and register it (either globally or
locally in a site).

Let's see whether we get the customized template now::

  >>> custom.render('templates', 'test1.st', {'thing': 'planet'})
  u'Goodbye planet'

Broken custom template
----------------------

If a custom template cannot be compiled, the system falls back on the
filesystem template instead. We construct a broken custom template by
adding ``&`` to it::

  >>> original_source = root_db.get_source('test2.st')
  >>> source = original_source.replace('full of', 'filled with &')
  >>> mem_db.update('test2.st', source)

We try to render this template, but instead we'll see the original
template::

  >>> custom.render('templates', 'test2.st', {'thing': 'planets'})
  u"It's full of planets"

It could also be the case that the custom template can be compiled but
instead cannot be rendered. Let's construct one that expects ``thang``
instead of ``thing``::

  >>> source = original_source.replace('$thing', '$thang')
  >>> mem_db.update('test2.st', source)

When rendering the system will notice the RenderError and fall back on
the original uncustomized template for rendering::

  >>> custom.render('templates', 'test2.st', {'thing': 'planets'})
  u"It's full of planets"

Checking which template languages are recognized
------------------------------------------------

We can check which template languages are recognized::

  >>> languages = custom.recognized_languages()
  >>> sorted(languages)
  [(u'.st', <class 'StringTemplate'>)]

When we register another language::

  >>> class StringTemplate2(StringTemplate):
  ...   pass
  >>> custom.register_language(StringTemplate2, extension='.st2')

It will show up too::

  >>> languages = custom.recognized_languages()
  >>> sorted(languages)
  [(u'.st', <class 'StringTemplate'>), (u'.st2', <class 'StringTemplate2'>)]

Retrieving which templates can be customized
--------------------------------------------

For the filesystem-level templates it is possible to get a data
structure that indicates which templates can be customized. This is
useful when constructing a UI. This data structure is designed to be
easily useful as JSON so that a client-side UI can be constructed.

Let's retrieve the customization database for our collection::

  >>> l = custom.structure('templates')
  >>> from pprint import pprint
  >>> pprint(l)
  [{'extension': '.st',
    'name': 'test1',
    'path': 'test1.st',
    'template': 'test1.st'},
   {'extension': '.st',
    'name': 'test2',
    'path': 'test2.st',
    'template': 'test2.st'}]

Samples
-------

In a customization user interface it is useful to be able to test the
template. Sometimes this can be done with live data coming from the
software, but in other cases it is more convenient to try it on some
representative sample data. This sample data needs to be in the format
as expected as the argument when calling the template.

Just like a template language is stored as plain text on the
filesystem, sample data can also be stored as plain text on the file
system. The format of this plain text is its data language. Examples
of data languages are JSON and XML.

For the purposes of demonstration, we'll define a simle data language
that can turn into a dictionary a data file with key value pairs like
this::

  >>> data = """\
  ... a: b
  ... c: d
  ... e: f
  ... """

Now we define a function that can parse this data into a dictionary::

  >>> def parse_dict_data(data):
  ...    result = {}
  ...    for line in data.splitlines():
  ...        key, value = line.split(':')
  ...        key = key.strip()
  ...        value = value.strip()
  ...        result[key] = value
  ...    return result
  >>> d = parse_dict_data(data)
  >>> sorted(d.items())
  [('a', 'b'), ('c', 'd'), ('e', 'f')]

The idea is that we can ask a particular template for those sample inputs
that are available for it. Let's for instance check for sample inputs 
available for ``test1.st``::

  >>> root_db.get_samples('test1.st')
  {}

There's nothing yet.

In order to get samples to work, we first need to register the data
language::

  >>> custom.register_data_language(parse_dict_data, '.d')

Files with the extension ``.d`` can now be recognized as containing
sample data.

We still need to tell the system that StringTemplate templates in
particular can be expected to find sample data with this extension. In
order to express this, we need to register the StringTemplate language
again with an extra argument that indicates this (``sample_extension``)::

  >>> custom.register_language(StringTemplate,
  ...    extension='.st', sample_extension='.d')

Now we can actually look for samples. Of course there still aren't
any as we haven't created any ``.d`` files yet::

  >>> root_db.get_samples('test1.st')
  {}

We need a pattern to associate a sample data file with a template
file.  The convention used is that a sample data file is in the same
directory as the template file, and starts with the name of the
template followed by a dash (``-``). Following the dash should be the
name of the sample itself. Finally, the extension should be the sample
extension. Here we create a sample file for the ``test1.st``
template::

  >>> test1_path = os.path.join(templates_path, 'test1-sample1.d')
  >>> f = open(test1_path, 'w')
  >>> f.write('thing: galaxy')
  >>> f.close()

Now when we ask for the samples available for our ``test1`` template,
we should see ``sample1``::

  >>> r = root_db.get_samples('test1.st')
  >>> r
  {'sample1': {'thing': 'galaxy'}}

By definition, we can use the sample data for a template and pass it
to the template itself::

  >>> template = custom.lookup('templates', 'test1.st')
  >>> template(r['sample1'])
  u'Goodbye galaxy'

Testing a template
------------------

In a user interface it can be useful to be able to test whether the
template compiles and renders. ``hurry.custom`` therefore implements a
``check`` function that does so. This function raises an error
(``CompileError`` or ``RenderError``), and passes silently if there is no
problem.

Let's first try it with a broken template::

  >>> custom.check('templates', 'test1.st', 'foo & bar')
  Traceback (most recent call last):
    ...
  CompileError: & in template!

We'll now try it with a template that does compile but doesn't work
with ``sample1``, as no ``something`` is supplied::

  >>> custom.check('templates', 'test1.st', 'hello $something')
  Traceback (most recent call last):
    ...
  RenderError: 'something'

Error handling
--------------

Let's try to render a template in a collection that doesn't exist. We
get a message that the template database could not be found::

  >>> custom.render('nonexistent', 'dummy.st', {})
  Traceback (most recent call last):
    ...
  ComponentLookupError: (<InterfaceClass hurry.custom.interfaces.ITemplateDatabase>, 'nonexistent')

Let's render a non-existent template in an existing database. We get
the lookup error of the deepest database, which is assumed to be the
filesystem::

  >>> custom.render('templates', 'nonexisting.st', {})
  Traceback (most recent call last):
    ...
  IOError: [Errno 2] No such file or directory: '.../nonexisting.st'

Let's render a template with an unrecognized extension::

  >>> custom.render('templates', 'dummy.unrecognized', {})
  Traceback (most recent call last):
    ...
  ComponentLookupError: (<InterfaceClass hurry.custom.interfaces.ITemplate>, '.unrecognized')

The template language ``.unrecognized`` could not be found. Let's make the
file exist; we should get the same result::

  >>> unrecognized = os.path.join(templates_path, 'dummy.unrecognized')
  >>> f = open(unrecognized, 'w')
  >>> f.write('Some weird template language')
  >>> f.close()

Now let's look at it again::

  >>> template = custom.render('templates', 'dummy.unrecognized', {})
  Traceback (most recent call last):
    ...
  ComponentLookupError: (<InterfaceClass hurry.custom.interfaces.ITemplate>, '.unrecognized')

If we try to look up a template in the root collection with a
CompileError in it, we'll get a CompileError::

  >>> compile_error = os.path.join(templates_path, 'compileerror.st')
  >>> f = open(compile_error, 'w')
  >>> f.write('A & compile error')
  >>> f.close()
  >>> compile_error_template = custom.lookup('templates', 'compileerror.st')
  Traceback (most recent call last):
    ...
  CompileError: & in template!

The same applies to trying to render it::

  >>> custom.render('templates', 'compileerror.st', {})
  Traceback (most recent call last):
    ...
  CompileError: & in template!

If we try to render a template in the root collection we get a RenderError::
  
  >>> render_error = os.path.join(templates_path, 'rendererror.st')
  >>> f = open(render_error, 'w')
  >>> f.write('A $thang')
  >>> f.close()
  >>> custom.render('templates', 'rendererror.st', {'thing': 'thing'})
  Traceback (most recent call last):
    ...
  RenderError: u'thang'


We'll get a ComponentLookupError if we look for a collection with an
unknown id::

  >>> custom.collection('unknown_id')
  Traceback (most recent call last):
    ...
  ComponentLookupError: (<InterfaceClass hurry.custom.interfaces.ITemplateDatabase>, 'unknown_id')

We also can't look for a next collection if the id we specify is
unknown::

  >>> custom.next_collection('unknown_id', mem_db)
  Traceback (most recent call last):
    ...
  ComponentLookupError: No more utilities for <InterfaceClass hurry.custom.interfaces.ITemplateDatabase>, 'unknown_id' have been found.

Similarly we can't get a root collection if the id is unknown::

  >>> custom.root_collection('unknown_id')
  Traceback (most recent call last):
    ...
  ComponentLookupError: (<InterfaceClass hurry.custom.interfaces.ITemplateDatabase>, 'unknown_id')

