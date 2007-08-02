import sys, os
import ZConfig
import zope.event
import App.config
import Zope2.Startup
from zope.app.wsgi import WSGIPublisherApplication
from zope.app.appsetup.interfaces import DatabaseOpened, ProcessStarting

def application_factory(global_conf, conf='zope.conf'):
    # load 'zope.conf' configuration
    schema_xml = os.path.join(
        os.path.dirname(Zope2.Startup.__file__), 'zopeschema.xml')
    schema = ZConfig.loadSchema(schema_xml)
    options, handlers = ZConfig.loadConfig(
        schema, os.path.join(global_conf['here'], conf))

    # read global settings from configuration file
    App.config.setConfiguration(options)

    starter = Zope2.Startup.get_starter()
    starter.setConfiguration(options)

    starter.setupInitialLogging()
    starter.setupLocale()
    starter.setupSecurityOptions()
    starter.setupInterpreter()
    Zope2.startup()  # open ZODB, initialize Products, etc.
    starter.setupFinalLogging()

    db = Zope2.DB  # XXX ick
    zope.event.notify(ProcessStarting())
    return WSGIPublisherApplication(db)
