from Acquisition import Implicit
from OFS.SimpleItem import Item
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.TypesTool import TypeInformation
from Products.CMFCore.TypesTool import FactoryTypeInformation

class DummyMethod:
    """
    A dummy callable method
    """
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name
    def __call__(self):
        return self.name

class DummyContent( PortalContent, Item ):
    """
    A Dummy piece of PortalContent
    """
    meta_type = 'Dummy'
    url = 'foo_url'
    after_add_called = before_delete_called = 0

    def __init__( self, id='dummy', *args, **kw ):
        self.id = id
        self._args = args
        self._kw = {}
        self._kw.update( kw )

        self.reset()
        self.catalog = kw.get('catalog',0)
        self.url = kw.get('url',None)

    def manage_afterAdd( self, item, container ):
        self.after_add_called = 1
        if self.catalog:
            PortalContent.manage_afterAdd( self, item, container )

    def manage_beforeDelete( self, item, container ):
        self.before_delete_called = 1
        if self.catalog:
            PortalContent.manage_beforeDelete( self, item, container )
    
    def absolute_url(self):
       return self.url

    def reset( self ):
        self.after_add_called = self.before_delete_called = 0

    # Make sure normal Database export/import stuff doesn't trip us up.
    def _getCopy( self, container ):        
        return DummyContent( self.id, catalog=self.catalog )

    def _safe_get(self,attr):
        if self.catalog:
            return getattr(self,attr,'')
        else:
            return getattr(self,attr)

    def Title( self ):
        return self.title

    def Creator( self ):
        return self._safe_get('creator')

    def Subject( self ):
        return self._safe_get('subject')

    def Description( self ):
        return self.description

    def created( self ):
        return self._safe_get('created_date')

    def modified( self ):
        return self._safe_get('modified_date')
    
    def Type( self ):
        return 'Dummy Content'

def addDummy( self, id ):
    """
    Constructor method for DummyContent
    """
    self._setObject( id, DummyContent() )

class DummyFactory:
    """
    Dummy Product Factory
    """
    def __init__( self, folder ):
        self._folder = folder

    def addFoo( self, id, *args, **kw ):
        if self._folder._prefix:
            id = '%s_%s' % ( self._folder._prefix, id )
        foo = apply( DummyContent, ( id, ) + args, kw )
        self._folder._setOb( id, foo )
        if self._folder._prefix:
            return id

    __roles__ = ( 'FooAdder', )
    __allow_access_to_unprotected_subobjects__ = { 'addFoo' : 1 }


class DummyTypeInfo(TypeInformation):
    """ Dummy class of type info object """
    meta_type = "Dummy Test Type Info"

DummyFTI = FactoryTypeInformation( 'Dummy',
                                   meta_type=DummyContent.meta_type,
                                   product='CMFDefault',
                                   factory='addDocument',
                                   actions= ( { 'name'          : 'View',
                                                'action'        : 'view',
                                                'permissions'   : ('View', ) },
                                              { 'name'          : 'View2',
                                                'action'        : 'view2',
                                                'permissions'   : ('View', ) },
                                              { 'name'          : 'Edit',
                                                'action'        : 'edit',
                                                'permissions'   : ('forbidden permission',)
                                                }
                                              )
                                   )

class DummyFolder( Implicit ):
    """
        Dummy Container for testing
    """
    def __init__( self, fake_product=0, prefix='' ):
        self._prefix = prefix

        if fake_product:
            self.manage_addProduct = { 'FooProduct' : DummyFactory( self ) }

        self._objects = {}

    def _setOb( self, id, obj ):
        self._objects[id] = obj

    def _getOb( self, id ):
        return self._objects[id]

class DummyMembershipTool:
    def __init__(self, anon=1):
        self.anon = anon 

    def isAnonymousUser(self):
        return self.anon 

    def getAuthenticatedMember(self):
        return "member"
  
