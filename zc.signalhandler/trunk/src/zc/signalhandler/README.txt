===========================
Registering signal handlers
===========================

This package provides a way to register signal handlers from a ZConfig
configuration.  There is a ZConfig component which is converted to a
mapping of signal names to a list of handler functions.  The handlers
take no arguments.

The configuration section that provides signal handling information is
considered a "product configuration" section for Zope 3, so let's
create a simple schema that accepts product configurations::

  >>> schema_text = '''\
  ... <schema>
  ...   <abstracttype name="zope.product.base"/>
  ...   <section type="zope.product.base"
  ...            attribute="siginfo"
  ...            name="*"
  ...            />
  ... </schema>
  ... '''

  >>> import os
  >>> import signal
  >>> import StringIO
  >>> import ZConfig

  >>> schema = ZConfig.loadSchemaFile(StringIO.StringIO(schema_text))

A sample configuration can simple import the ``zc.signalhandler``
component and use it::

  >>> config_text = '''
  ...
  ... %import zc.signalhandler
  ...
  ... <signalhandlers foo>
  ...   hup   zc.signalhandler.tests.sample_handler_1
  ...   hup   zc.signalhandler.tests.sample_handler_2
  ...   usr1  zc.signalhandler.tests.sample_handler_1
  ... </signalhandlers>
  ...
  ... '''

We can install some default behavior for a signal::

  >>> def some_behavior(sign, frame):
  ...     print "some old behavior"

  >>> old = signal.signal(signal.SIGUSR1, some_behavior)

Let's try loading our sample configuration::

  >>> config, config_handlers = ZConfig.loadConfigFile(
  ...     schema, StringIO.StringIO(config_text))

  >>> handlers = config.siginfo.handlers
  >>> sorted(handlers)
  ['SIGHUP', 'SIGUSR1']

  >>> import zc.signalhandler.tests

  >>> h1, h2 = handlers["SIGHUP"]
  >>> h1 is zc.signalhandler.tests.sample_handler_1
  True
  >>> h2 is zc.signalhandler.tests.sample_handler_2
  True

  >>> h1, = handlers["SIGUSR1"]
  >>> h1 is zc.signalhandler.tests.sample_handler_1
  True

At this point, the handlers are installed.  We can signal ourselves,
and see that the handler is triggered::

  >>> os.kill(os.getpid(), signal.SIGUSR1)
  handler 1

We can even trigger multiple handlers for a single signal::

  >>> os.kill(os.getpid(), signal.SIGHUP)
  handler 1
  handler 2

We can also uninstall the handlers::

  >>> config.siginfo.uninstall()

  >>> os.kill(os.getpid(), signal.SIGUSR1)
  some old behavior

Now let's restore the previous behavior of the signal::

  >>> x = signal.signal(signal.SIGUSR1, old)

The section value provides a couple of attributes that are used solely
to support the ``zope.app.appsetup.product`` APIs::

  >>> config.siginfo.getSectionName()
  'foo'

  >>> config.siginfo.mapping is config.siginfo
  True
