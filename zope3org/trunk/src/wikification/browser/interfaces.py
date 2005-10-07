__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.interface import Attribute

from zope.i18n import MessageIDFactory


_ = MessageIDFactory("zope3org.wikification")
          


class IWikiPage(Interface) :
    """ A wiki page that 'wikifies' a folder with ordinary HTML documents.
    
        See wikification/README.txt for a definition of what 
        'wikification' means and doctests of the methods of this class.
        
    """
   
        
class IWikiFolderPage(IWikiPage) :
    """ Wiki view for a container. """
    
class IWikiFilePage(IWikiPage) :
    """ Wiki view for a file. """
            
        
class IEditWikiPage(IWikiPage) :
    """ Edit view for a file. """

class ICreateWikiPage(IWikiPage) :
    """ Edit view for a folder. """