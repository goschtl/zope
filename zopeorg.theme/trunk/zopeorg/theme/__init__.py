from zope.i18nmessageid import MessageFactory as msgfac
from Products.Archetypes.public import process_types
from Products.Archetypes.public import listTypes
from Products.CMFCore.utils import ContentInit
from zopeorg.theme.config import PROJECTNAME

MessageFactory = msgfac("zopeorg.theme")
    
def initialize(context):
    import zopeorg.theme.content
    from zopeorg.theme import permissions
    listOfTypes=listTypes(PROJECTNAME)
    (content_types, constructors, ftis)=process_types(listOfTypes, PROJECTNAME)
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        ContentInit(
            kind,
            content_types      = (atype,),
            # Add permissions look like perms.Add{meta_type}
            permission         = getattr(permissions, "Add%s" % atype.meta_type),
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context) 

