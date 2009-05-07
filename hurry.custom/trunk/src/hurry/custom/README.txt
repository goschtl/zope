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

Registering a template language
-------------------------------

In order to register a new push-only template we need to provide a
factory that takes the template text (which could be compiled down
further). Instantiating the factory should result in a callable that
takes the input data (in whatever format is native to the template
language). The ``ITemplate`` interface defines such an object::

  >>> from hurry.custom.interfaces import ITemplate

For the purposes of demonstrating the functionality in this package,
we supply a very simplistic push-only templating language, based on
template strings as provided by the Python ``string`` module::

  >>> import string
  >>> from zope.interface import implements
  >>> class StringTemplate(object):
  ...    implements(ITemplate)
  ...    def __init__(self, text):
  ...        self.source = text
  ...        self.template = string.Template(text)
  ...    def __call__(self, input):
  ...        return self.template.substitute(input)

Let's demonstrate it. To render the template, simply call it with the
data as an argument::

  >>> template = StringTemplate('Hello $thing')
  >>> template({'thing': 'world'})
  'Hello world'

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

In order for the system to work, we need to register this collection
of templates on the filesystem. We need to supply a globally unique
collection id, the templates path, and (optionally) a title::

  >>> custom.register_collection(id='templates', path=templates_path)

We can now look up the template in this collection::

  >>> template = custom.lookup('templates', 'test1.st')

We got our proper template::

  >>> template.source
  u'Hello $thing'

As we can see the source text of the template was interpreted as a
UTF-8 string. The template source should always be in unicode format
(or in plain ASCII).

  >>> template({'thing': 'world'})
  u'Hello world'

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

  >>> from zope import component
  >>> from hurry.custom.interfaces import ITemplateDatabase
  >>> root_db = component.getUtility(ITemplateDatabase, name='templates')

Let's now register a customization database for our collection, in a
particular site. This means in such a site, the new customized
template database will be used (with a fallback on the original one if
no customization can be found).

Let's create a site first::

  >>> site1 = DummySite(id=1)

We register a customization database for our collection named
``templates``. For the purposes of testing we will use an in-memory
database::

  >>> mem_db = custom.InMemoryTemplateDatabase('templates', 'Templates')
  >>> sm1 = site1.getSiteManager()
  >>> sm1.registerUtility(mem_db, provided=ITemplateDatabase, 
  ...   name='templates')

We go into this site::

  >>> setSite(site1)

We haven't placed any customization in the customization database
yet, so we'll see the same thing as before when we look up the
template::

  >>> template = custom.lookup('templates', 'test1.st')
  >>> template({'thing': "universe"})
  u'Bye universe'

Customization of a template
---------------------------

Now that we have a locally set up customization database, we can
customize the ``test1.st`` template. 

In this customization we change 'Bye' to 'Goodbye'::

  >>> source = template.source
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

  >>> template = custom.lookup('templates', 'test1.st')
  >>> template({'thing': 'planet'})
  u'Goodbye planet'

It is sometimes useful to be able to retrieve the original version of
the template, before customization::

  >>> template.original_source
  u'Bye $thing'

This could be used to implement a "revert" functionality in a
customization UI, for instance.

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
    'template': 'test1.st'}]

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

  >>> template.samples()
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

  >>> template.samples()
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

  >>> r = template.samples()
  >>> r
  {'sample1': {'thing': 'galaxy'}}

By definition, we can use the sample data for a template and pass it
to the template itself::

  >>> template(r['sample1'])
  u'Goodbye galaxy'

Error handling
--------------

Let's try to look up a template in a collection that doesn't exist. We
get a message that the template database could not be found::

  >>> custom.lookup('nonexistent', 'dummy.st')
  Traceback (most recent call last):
    ...
  ComponentLookupError: (<InterfaceClass hurry.custom.interfaces.ITemplateDatabase>, 'nonexistent')

Let's look up a non-existent template in an existing database. We get
the lookup error of the deepest database, which is assumed to be the
filesystem::

  >>> template = custom.lookup('templates', 'nonexisting.st')
  Traceback (most recent call last):
    ...
  IOError: [Errno 2] No such file or directory: '.../nonexisting.st'

Let's look up a template with an unrecognized extension::

  >>> template = custom.lookup('templates', 'dummy.unrecognized')
  Traceback (most recent call last):
    ...
  IOError: [Errno 2] No such file or directory: '.../dummy.unrecognized'

This of course happens because ``dummy.unrecognized`` doesn't exist. Let's
make it exist::

  >>> unrecognized = os.path.join(templates_path, 'dummy.unrecognized')
  >>> f = open(unrecognized, 'w')
  >>> f.write('Some weird template language')
  >>> f.close()

Now let's look at it again::

  >>> template = custom.lookup('templates', 'dummy.unrecognized')
  Traceback (most recent call last):
    ...
  ComponentLookupError: (<InterfaceClass hurry.custom.interfaces.ITemplate>, '.unrecognized')
