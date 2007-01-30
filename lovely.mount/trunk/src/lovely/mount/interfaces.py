from i18n import _
from zope import interface
from zope import schema
from zope.interface.common.mapping import IMapping
from zope.app.container.interfaces import IContainer

class IDBRoot(IMapping):

    dbName = schema.ASCII(title=_('Database Name'))

    
class IMountpointContainer(IContainer, IDBRoot):

    """a container which returns its values from another database"""

    dbName = schema.Choice(title=_('Database Name'),
                           vocabulary='Database Names')
