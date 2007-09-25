class MetaType:
    def get_property(self, name):
        """
            Get type information and metadata for property.
            Returns a MetaType
        """
    
    def is_collection(self):
        """Returns True if the represented type is a collection."""
    
    def get_type(self):
        """Returns the represented type"""
    
    def get_contained(self):
        """
            Throws an exception if represented type is not a collection, or
            the contained type if a collection
        """
    
    def get_size(self):
        """Returns the size of the collection or class if known"""

class Metadata:
    def __init__(self, engine):
        self.engine = engine
    
    def get_class(self, classname):
        """Returns a MetaType instance for the class."""