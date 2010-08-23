===========
Quick Entry
===========

The quick entry processor allows a user to efficiently specify multiple values
in one larger text block. The processor uses plugins to dynamically define the
commands to handle.

This type of input is not aimed at the average user, but at power users and
users that can be trained. The syntax is purposefully minimized to maximize
the input speed. This method of entry has been verified in a real life
setting.


Processor Plugins
-----------------

Let's start by looking at the processor plugins, which can handle one piece of
the quick entry text. The first plugin type can handle strings of the form:

  <shortName>=<value>

A base implementation of this plugin is provided by the package. Let's create
a plugin that can process a name:

  >>> from z3c.quickentry import plugin
  >>> class NamePlugin(plugin.ShortNamePlugin):
  ...     shortName = 'nm'
  ...     varName = 'name'

Any plugin is instantiated using an initial text and optionally a position
that is used during error reporting:

  >>> name = NamePlugin('nm=Stephan')
  >>> name
  <NamePlugin shortName='nm', varName='name'>

  >>> NamePlugin('nm=Stephan', 35)
  <NamePlugin shortName='nm', varName='name'>

You can now ask the plugin, whether it can process this text:

  >>> name.canProcess()
  True

  >>> NamePlugin('n=Stephan').canProcess()
  False
  >>> NamePlugin('Stephan').canProcess()
  False

Sometimes the processor adds more text later:

  >>> name.text += ' Richter'

Once all pieces have been processed by the quick entry processor, each
instantiated plugin gets processed. The result of this action is a dictionary:

  >>> name.process(None)
  {'name': u'Stephan Richter'}

The second type of plugin matches a regular expression to determine whether a
piece of text can be processed. Let's create a phone number plugin:

  >>> import re
  >>> class PhonePlugin(plugin.RegexPlugin):
  ...     regex = re.compile('^[0-9]{3}-[0-9]{3}-[0-9]{4}$')
  ...     varName = 'phone'

This plugin is also instantiated using an initial text:

  >>> phone = PhonePlugin('978-555-5300')
  >>> phone
  <PhonePlugin varName='phone'>

You can now ask the plugin, whether it can process this text:

  >>> name.canProcess()
  True

  >>> PhonePlugin('(978) 555-5300').canProcess()
  False
  >>> PhonePlugin('+1-978-555-5300').canProcess()
  False

Let's now process the plugin:

  >>> phone.process(None)
  {'phone': u'978-555-5300'}

If the text changes, so that the plugin cannot parse the text anymore, a
process error is raised:

  >>> phone.text += ' (ext. 2134)'
  >>> phone.process(None)
  Traceback (most recent call last):
  ...
  ProcessError: The regex did match anymore. Probably some text was added
                later that disrupted the pattern. (Position 0)


Finally let's have a look at a more advanced example. We would like to be able
to handle the string "<age><gender>" and parse it into 2 variables:

  >>> from z3c.quickentry import interfaces

  >>> class AgeGenderPlugin(plugin.BasePlugin):
  ...     regex = re.compile('([0-9]{1,3})([FM])')
  ...
  ...     def canProcess(self):
  ...         return self.regex.match(self.text) is not None
  ...
  ...     def process(self, context):
  ...         match = self.regex.match(self.text)
  ...         if match is None:
  ...            raise interfaces.ProcessError(self.position, u'Error here.')
  ...         return {'age': int(match.groups()[0]),
  ...                 'gender': unicode(match.groups()[1])}

Let's now make sure that the plugin can handle several strings:

  >>> AgeGenderPlugin('27M').canProcess()
  True
  >>> AgeGenderPlugin('8F').canProcess()
  True
  >>> AgeGenderPlugin('101F').canProcess()
  True
  >>> AgeGenderPlugin('27N').canProcess()
  False
  >>> AgeGenderPlugin('M').canProcess()
  False
  >>> AgeGenderPlugin('18').canProcess()
  False

Let's also make sure it is processed correctly:

  >>> from pprint import pprint
  >>> pprint(AgeGenderPlugin('27M').process(None))
  {'age': 27, 'gender': u'M'}
  >>> pprint(AgeGenderPlugin('8F').process(None))
  {'age': 8, 'gender': u'F'}
  >>> pprint(AgeGenderPlugin('101F').process(None))
  {'age': 101, 'gender': u'F'}

When an error occurs at any point during the processing, a process error must
be raised:

  >>> pprint(AgeGenderPlugin('27N').process(None))
  Traceback (most recent call last):
  ...
  ProcessError: Error here. (Position 0)

The plugin above used the ``BasePlugin`` class to minimize the
boilerplate. The base plugin requires you to implement the ``canProcess()``
and ``process()``:

  >>> base = plugin.BasePlugin('some text')

  >>> base.canProcess()
  Traceback (most recent call last):
  ...
  NotImplementedError

  >>> base.process(None)
  Traceback (most recent call last):
  ...
  NotImplementedError


Executing Plugins
-----------------

An optional feature of the package is the ability for the plugin to apply the
parsed data directly to a specified context. The simplest such case is to
simply set the attribute on the context. For this use case we have a mix-in
class:

  >>> class ExecutingAgeGenderPlugin(AgeGenderPlugin, plugin.SetAttributeMixin):
  ...     pass

Let's now create a person on which the attributes can be stored:

  >>> class Person(object):
  ...     name = None
  ...     phone = None
  ...     age = None
  ...     gender = None
  >>> stephan = Person()

Let's now apply the executing age/gender plugin onto the person:

  >>> stephan.age
  >>> stephan.gender

  >>> ExecutingAgeGenderPlugin('27M').apply(stephan)

  >>> stephan.age
  27
  >>> stephan.gender
  u'M'


Processors
----------

The processor collects several plugins and handles one large chunk of quick
entry text. Let's create a processor for the plugins above, using the default
whitespace character as field separator:

  >>> from z3c.quickentry import processor
  >>> info = processor.BaseProcessor()
  >>> info.plugins = (NamePlugin, PhonePlugin, AgeGenderPlugin)

The lowest level step of the processor is the parsing of the text; the result
is a sequence of plugin instances:

  >>> info.parse('nm=Stephan 27M')
  [<NamePlugin shortName='nm', varName='name'>, <AgeGenderPlugin '27M'>]

Let's now parse and process a simple texts that uses some or all plugins:

  >>> pprint(info.process('nm=Stephan 27M'))
  {'age': 27, 'gender': u'M', 'name': u'Stephan'}

  >>> pprint(info.process('978-555-5300 27M'))
  {'age': 27, 'gender': u'M', 'phone': u'978-555-5300'}

  >>> pprint(info.process('nm=Stephan 978-555-5300 27M'))
  {'age': 27, 'gender': u'M', 'name': u'Stephan', 'phone': u'978-555-5300'}

Note that you can also have names that contain spaces, because the last name
cannot be matched to another plugin:

  >>> pprint(info.process('nm=Stephan Richter 27M'))
  {'age': 27, 'gender': u'M', 'name': u'Stephan Richter'}

Optionally, you can also provide a processing context that can be used to look
up values (for example vocabularies):

  >>> pprint(info.process('nm=Stephan Richter 27M', context=object()))
  {'age': 27, 'gender': u'M', 'name': u'Stephan Richter'}

Let's now change the separation character to a comma:

  >>> info.separationCharacter = ','
  >>> pprint(info.process('nm=Stephan Richter,27M', context=object()))
  {'age': 27, 'gender': u'M', 'name': u'Stephan Richter'}

But what happens, if no plugin can be found. Then a process error is raised:

  >>> info.process('err=Value', context=object())
  Traceback (most recent call last):
  ...
  ProcessError: No matching plugin found. (Position 0)


Executing Processors
--------------------

These processors can apply all of the plugins on a context. Let's convert the
remaining plugins to be executable:

  >>> class ExecutingNamePlugin(NamePlugin, plugin.SetAttributeMixin):
  ...     pass

  >>> class ExecutingPhonePlugin(PhonePlugin, plugin.SetAttributeMixin):
  ...     pass

Let's now create a new user and create an executing processor:

  >>> stephan = Person()

  >>> proc = processor.ExecutingBaseProcessor()
  >>> proc.plugins = (
  ...     ExecutingNamePlugin, ExecutingPhonePlugin, ExecutingAgeGenderPlugin)

  >>> proc.apply('nm=Stephan 978-555-5300 27M', stephan)

  >>> stephan.name
  u'Stephan'
  >>> stephan.phone
  u'978-555-5300'
  >>> stephan.age
  27
  >>> stephan.gender
  u'M'
