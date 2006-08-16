==========================================
Pluggable sample data framework for Lovely
==========================================

There are several goals to this framework:

- provide the developers with an automatic setup that is close to
  real-world use.

- provide the users with an easy setup for evaluation with plausible data

- provide the user a management interface for different sample generators

The framework is pluggable and allows the creators of generator
extensions to provide their own plugins that generate sample data for
those extensions.


Generators
----------

A generator generates a setup.

  >>> from zope import interface
  >>> from zope import component
  >>> from z3c.sampledata.interfaces import ISampleDataPlugin

  >>> class GeneratePrincipals(object):
  ...     interface.implements(ISampleDataPlugin)
  ...     name = 'z3c.principals'
  ...     dependencies = []
  ...     schema = None
  ...     def generate(self, context, param={}, seed=None):
  ...         if context != 'This is a site':
  ...             print 'Expected string "This is a site" !'
  >>> principalPlugin = GeneratePrincipals()

For the sample manager the plugin must be registered as a utility.

  >>> component.provideUtility(principalPlugin, ISampleDataPlugin,'z3c.principals')

For our tests we provide another generator :

  >>> class GenerateSite(object):
  ...     interface.implements(ISampleDataPlugin)
  ...     name = 'z3c.site'
  ...     dependencies = []
  ...     schema = None
  ...     def generate(self, context, param={}, seed=None):
  ...         return 'This is a site'
  >>> sitePlugin = GenerateSite()
  >>> component.provideUtility(sitePlugin, ISampleDataPlugin,'z3c.site')


Generator Manager
-----------------

A generator manager groups a collection of generators and allows to define
dependencies between generator.

  >>> from z3c.sampledata import Manager
  >>> manager = Manager('manager', '')

Now we can add generators to the manager.
In addition to the "hardwired" dependencies in each generator it is possible
to add dependencies in the generator manager.

  >>> manager.add('z3c.principals',
  ...             dependsOn=['z3c.site',],
  ...             contextFrom='z3c.site')

A manager provides it's generators.

  >>> manager.generators.keys()
  ['z3c.principals']

We can tell the manager to generate all samples.
There is no need to add the sample generator 'z3c.site', it is added
automatically because of the dependency of 'z3c.principals'.

  >>> infos = manager.generate(context=None, param={}, seed='something')
  >>> [info.name for info in infos]
  ['z3c.site', 'z3c.principals']

Cycles are detected.

  >>> manager = Manager('manager', '')
  >>> manager.add('z3c.principals',
  ...             dependsOn=['z3c.site',],
  ...             contextFrom='z3c.site')
  >>> manager.add('z3c.site',
  ...             dependsOn=['z3c.principals',])

  >>> infos = manager.generate(context=None, param={}, seed='something')
  Traceback (most recent call last):
  ...
  CyclicDependencyError: cyclic dependency at 'z3c.principals'

A test for a complex dependency.

  >>> class Generator(object):
  ...     interface.implements(ISampleDataPlugin)
  ...     name = 'generator'
  ...     dependencies = []
  ...     schema = None
  ...     def generate(self, context, param={}, seed=None):
  ...         return 'I am a generator'
  >>> component.provideUtility(Generator(), ISampleDataPlugin,'g.1')
  >>> component.provideUtility(Generator(), ISampleDataPlugin,'g.2')
  >>> component.provideUtility(Generator(), ISampleDataPlugin,'g.3')
  >>> manager = Manager('manager', '')
  >>> manager.add('g.1')
  >>> manager.add('g.2', contextFrom='g.1')
  >>> manager.add('g.3', dependsOn=['g.2', 'g.1'], contextFrom='g.1')
  >>> infos = manager.generate(context=None, param={}, seed=None)
  >>> [info.name for info in infos]
  ['g.1', 'g.2', 'g.3']


BuiltIn sample generators
-------------------------

To support functional tests some basic sample generators are already
implemented.

Site
~~~~

Creates a simple folder and makes it a site.

  >>> from z3c.sampledata.site import SampleSite
  >>> component.provideUtility(SampleSite(),
  ...                          ISampleDataPlugin,
  ...                          'z3c.sampledata.site')
  >>> manager = Manager('manager', '')
  >>> manager.add('z3c.sampledata.site')
  >>> from zope.app.folder.folder import Folder
  >>> baseContext = Folder()
  >>> infos = manager.generate(context=baseContext, param={'sitename':'test'}, seed=None)
  >>> [info.name for info in infos]
  ['z3c.sampledata.site']
  >>> 'test' in baseContext
  True


IntIds
~~~~~~

Creates an IntIds utility inside the site given as context.
This generator depends on the creation of a site.

  >>> from z3c.sampledata.site import SampleIntIds
  >>> component.provideUtility(SampleIntIds(),
  ...                          ISampleDataPlugin,
  ...                          'z3c.sampledata.intids')
  >>> manager.add('z3c.sampledata.intids',
  ...             contextFrom='z3c.sampledata.site',
  ...            )
  >>> baseContext = Folder()
  >>> infos = manager.generate(context=baseContext, param={'sitename':'intids'}, seed=None)
  >>> [info.name for info in infos]
  ['z3c.sampledata.site', 'z3c.sampledata.intids']
  >>> site = baseContext['intids']
  >>> site.getSiteManager()['default']['intid']
  <zope.app.intid.IntIds object at ...>


How do I create a sample data plugin?
-------------------------------------

In order to create a sample data plugin, you only have to register a
named utility that implements the interface
`z3c.sampledata.interfaces.ISampleDataPlugin`.

A plugin must provide :

 - name
 - dependencies on other plugins (list of names of ISampleDataPlugin utilities)
 - schema for the parameters


How to setup configuration for the generator manager
----------------------------------------------------

Configuration can be done using ZCML.

  <configure xmlns="http://namespaces.zope.org/zope">

    <configure
        xmlns:zcml="http://namespaces.zope.org/zcml"
        zcml:condition="have devmode">

      <utility
          factory=".SampleSite"
          provides="z3c.sampledata.interfaces.ISampleDataPlugin"
          name="z3c.site"
          />

      <utility
          factory=".SamplePrincipals"
          provides="z3c.sampledata.interfaces.ISampleDataPlugin"
          name="z3c.principals"
          />

      <SampleManager
        name="Site with principals"
        >
        <generator name="z3c.site" />
        <generator
          name="z3c.principal"
          dependsOn="z3c.site"
          contextFrom="z3c.site" />
      </SampleManager>

    </configure>

  </configure>


Data Generator
==============

This package implements the base functionality for data generators.
A data generator is used to provide the raw data for a sample generator.
Raw data can be read from text files in different ways.

  >>> from z3c.sampledata.data import DataGenerator
  >>> generator = DataGenerator(55)

The generator can read data lines from files.

  >>> generator.readLines('testlines.txt')
  [u'Line 1', u'Another line']

The generator can read data from CSV files.

  >>> generator.readCSV('testlines.csv')
  [['Line 1', 'Col 2'], ['Another line', 'Another Col']]

The generator can read a list of files from a path :

  >>> import os
  >>> generator.files(os.path.dirname(__file__))
  ['...README.txt', ...]

