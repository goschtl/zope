import zope.schema
from z3c.zalchemy.interfaces import ISQLAlchemyObjectContained, ISQLAlchemyContainer
from zope.app.container.constraints import contains, containers
from zope.interface import Interface, Attribute

class IHelloWorldFragment(ISQLAlchemyObjectContained):
    """Information about a hello world message"""
    
    message_id = Attribute("The ID of the parent message")

    what = zope.schema.TextLine(
        title=u'What',
        description=u'Type of message',
        required=True)
        
        
class IHelloWorldMessage4(ISQLAlchemyContainer,ISQLAlchemyObjectContained):
    """Information about a hello world message"""

    id = Attribute("The ID of the Message")
    
    fragments = Attribute("The contained Message fragments")
    
    who = zope.schema.TextLine(
        title=u'Who',
        description=u'Name of the person getting the message',
        required=True)
    contains(IHelloWorldFragment)


class IMessageContainer4(ISQLAlchemyContainer):
    """A container for hello world message mbjects"""
    contains(IHelloWorldMessage4)
    
