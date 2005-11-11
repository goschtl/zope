import sys
import Globals # this has side effects that require it to be imported early

# pkg_resource monkeypatching (if necessary) needs to happen before
# Products.Basket.utils is imported
try:
    # use the system-installed pkg_resources if possible
    import pkg_resources
except ImportError:
    # else use our "hardcoded" version if it doesn't exist in the user's
    # Python installation and stick it into sys.modules
    import pkg_resources_0_6a7 as pkg_resources
    sys.modules['pkg_resources'] = pkg_resources

# Poke the resource classes into the Zope package tree where they will 
# wind up in a future zope version, maybe
import resource

Globals.ImageResource = resource.ImageResource
Globals.DTMLResource = resource.DTMLResource

from Products import PageTemplates
PageTemplates.PageTemplateResource = resource.PageTemplateResource

# Prevent anyone from importing from here
del resource.ImageResource
del resource.DTMLResource
del resource.PageTemplateResource

from Products.Basket.basket import Basket

the_basket = Basket()
the_basket.preinitialize()
initialize = the_basket.initialize

