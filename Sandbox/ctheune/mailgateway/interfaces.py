from zope.interface import Interface, Attribute

class IMailReceivedEvent(Interface):

    mail = Attribute("The email as parsed RFC2822 message.")
    received_by = Attribute("A list of components who received this mail.")

