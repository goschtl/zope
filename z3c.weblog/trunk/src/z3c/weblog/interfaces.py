from zope.interface import Interface
from zope.schema import Text, TextLine, Field

from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.interfaces import IContained, IContainer
from zope.app.content.interfaces import IContentType
from zope.dublincore.interfaces import IDCDescriptiveProperties
from persistent.interfaces import IPersistent
from zope.app.file.interfaces import IFile

class IEntry(IPersistent):

    """A Entry for a Weblog"""

    id = TextLine(
        title = u"Unique Identifier",
        description = u"A unique identifier that never changes",
        readonly = True,
        required = True,
    )

    content = Text(
        title = u"Entry Content",
        description = u"Content for the Entry",
        default = u"",
        required = True,
        )


class IWeblog(IContainer):

    """A Weblog"""

    def __setitem__(name, object):
        """Add an Entry"""

    __setitem__.precondition = ItemTypePrecondition(IEntry)


class IEntryContained(IContained):

    """Interface that specifies what can contain Entrys"""

    __parent__ = Field(
        constraint=ContainerTypesConstraint(IWeblog, IEntry),
        )
    

class IDCEntry(IEntry, IDCDescriptiveProperties):

    """Entry with support for Dublin Core"""


class IDCWeblog(IWeblog, IDCDescriptiveProperties):

    """Weblog with DC"""

