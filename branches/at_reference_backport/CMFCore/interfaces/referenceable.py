from Interface import Attribute

try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

class IReferenceable(Interface):
    """this object is referenceable"""
    
    def UID():
        """ Unique ID """

    def getRefs():
        """get all the referenced objects for this object"""

    def getBRefs():
        """get all the back referenced objects for this object"""

    def reference_url():
        """like absoluteURL, but return a link to the object with this UID"""

    def hasRelationshipTo(target, relationship=None):
        """test is a relationship exists between objects"""

    def addReference(target, relationship=None, **kwargs):
        """add a reference to target. kwargs are metadata"""

    def deleteReference(target, relationship=None):
        """delete a ref to target"""

    def deleteReferences(relationship=None):
        """delete all references from this object"""

    def getRelationships():
        """list all the relationship types this object has refs for"""
