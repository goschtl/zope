from zope.component import getService
from zope.configuration.action import Action
from zope.app.services.servicenames import SQLDatabaseConnections

def connectionhandler(_context, name, component, dsn):

    component = _context.resolve(component)

    connection = component(dsn)

    return [
        Action(
            discriminator = ('provideConnection', name),
            callable = provideConnection,
            args = (name, connection),
            )
        ]

def provideConnection(name, connection):
    getService(None, SQLDatabaseConnections).provideConnection(name, connection)

