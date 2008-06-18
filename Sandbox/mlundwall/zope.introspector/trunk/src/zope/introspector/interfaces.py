from zope.interface import Interface

class IRegistryInfo(Interface):
    """Keeps information about the Component registry.
    """
    def getAllRegistrations():
        """ Returns a list of everything registered in the component registry. 
        """
    
    def getAllUtilities():
        """ Returns a list of all utilities registered in the component registery. 
        """
        
    def getAllAdapters():
        """ Returns a list of all adapters registered in the component registery. 
        """
    
    def getAllHandlers():
        """ Returns a list of all handlers registered in the component registery. 
        """
        
    def getAllSubscriptionAdapters():
        """ Returns a list of all handlers registered in the component registery. 
        """
        
    def getRegistrationsForInterface(searchString, types):
        """ Searches the component registry for any interface with searchString in the name...
            Returns a list of component objects.
        """
        
    def getAllInterfaces():
        """ Returns a dictionary with all interfaces...
            {'zope': 
                    {'app':
                            {'apidoc': [...],
                             'applicationcontrol': [...],
                             },
                    'component': [...],
                    },
            'docutils': [...],
            }
        """
        
class IRegistrySearch(Interface):
    """ Adapter interface that takes care of doing searches in different types of registry registrations.
    """
    
    def __init__(registration):
        """ Registers the registration in the adapter...
        """
        
    def searchRegistration(string, caseSensitive):
        """ Implements the search...
            returns True or False
        """
        
    def getInterfaces():
        """ Returns a list with the interfaces involved in this registration
        """
        
    def getObject():
        """ Returns the registration
        """