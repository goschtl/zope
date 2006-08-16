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
  >>> from lovely.sampledata.interfaces import ISampleDataPlugin

  >>> class GeneratePrincipals(object):
  ...     interface.implements(ISampleDataPlugin)
  ...     name = 'lovely.principals'
  ...     dependencies = []
  ...     schema = None
  ...     def generate(self, context, param={}, seed=None):
  ...         if context != 'This is a site':
  ...             print 'Expected string "This is a site" !'
  >>> principalPlugin = GeneratePrincipals()

For the sample manager the plugin must be registered as a utility.

  >>> component.provideUtility(principalPlugin, ISampleDataPlugin,'lovely.principals')

For our tests we provide another generator :

  >>> class GenerateSite(object):
  ...     interface.implements(ISampleDataPlugin)
  ...     name = 'lovely.site'
  ...     dependencies = []
  ...     schema = None
  ...     def generate(self, context, param={}, seed=None):
  ...         return 'This is a site'
  >>> sitePlugin = GenerateSite()
  >>> component.provideUtility(sitePlugin, ISampleDataPlugin,'lovely.site')


Generator Manager
-----------------

A generator manager groups a collection of generators and allows to define
dependencies between generator.

  >>> from lovely.sampledata import Manager
  >>> manager = Manager('manager', '')

Now we can add generators to the manager.
In addition to the "hardwired" dependencies in each generator it is possible
to add dependencies in the generator manager.

  >>> manager.add('lovely.principals',
  ...             dependsOn=['lovely.site',],
  ...             contextFrom='lovely.site')

A manager provides it's generators.

  >>> manager.generators.keys()
  ['lovely.principals']

We can tell the manager to generate all samples.
There is no need to add the sample generator 'lovely.site', it is added
automatically because of the dependency of 'lovely.principals'.

  >>> infos = manager.generate(context=None, param={}, seed='something')
  >>> [info.name for info in infos]
  ['lovely.site', 'lovely.principals']

Cycles are detected.

  >>> manager = Manager('manager', '')
  >>> manager.add('lovely.principals',
  ...             dependsOn=['lovely.site',],
  ...             contextFrom='lovely.site')
  >>> manager.add('lovely.site',
  ...             dependsOn=['lovely.principals',])

  >>> infos = manager.generate(context=None, param={}, seed='something')
  Traceback (most recent call last):
  ...
  CyclicDependencyError: cyclic dependency at 'lovely.site'

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

  >>> from lovely.sampledata.site import SampleSite
  >>> component.provideUtility(SampleSite(),
  ...                          ISampleDataPlugin,
  ...                          'lovely.sampledata.site')
  >>> manager = Manager('manager', '')
  >>> manager.add('lovely.sampledata.site')
  >>> from zope.app.folder.folder import Folder
  >>> baseContext = Folder()
  >>> infos = manager.generate(context=baseContext, param={'sitename':'test'}, seed=None)
  >>> [info.name for info in infos]
  ['lovely.sampledata.site']
  >>> 'test' in baseContext
  True


IntIds
~~~~~~

Creates an IntIds utility inside the site given as context.
This generator depends on the creation of a site.

  >>> from lovely.sampledata.site import SampleIntIds
  >>> component.provideUtility(SampleIntIds(),
  ...                          ISampleDataPlugin,
  ...                          'lovely.sampledata.intids')
  >>> manager.add('lovely.sampledata.intids',
  ...             contextFrom='lovely.sampledata.site',
  ...            )
  >>> baseContext = Folder()
  >>> infos = manager.generate(context=baseContext, param={'sitename':'intids'}, seed=None)
  >>> [info.name for info in infos]
  ['lovely.sampledata.site', 'lovely.sampledata.intids']
  >>> site = baseContext['intids']
  >>> site.getSiteManager()['default']['intid']
  <zope.app.intid.IntIds object at ...>


How do I create a sample data plugin?
-------------------------------------

In order to create a sample data plugin, you only have to register a
named utility that implements the interface
`lovely.sampledata.interfaces.ISampleDataPlugin`.

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
          provides="lovely.sampledata.interfaces.ISampleDataPlugin"
          name="lovely.site"
          />

      <utility
          factory=".SamplePrincipals"
          provides="lovely.sampledata.interfaces.ISampleDataPlugin"
          name="lovely.principals"
          />

      <SampleManager
        name="Site with principals"
        >
        <generator name="lovely.site" />
        <generator
          name="lovely.principal"
          dependsOn="lovely.site"
          contextFrom="lovely.site" />
      </SampleManager>

    </configure>

  </configure>


Data Generator
==============

This package implements the base functionality for data generators.
A data generator is used to provide the raw data for a sample generator.
Raw data can be read from text files in different ways.

  >>> from lovely.sampledata.data import DataGenerator
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

