from Products.ZCatalog.ZCatalog import manage_addZCatalog
from Products.CMFCore.ReferenceCatalog import manage_addReferenceCatalog
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.reference_config import *


def install_UIDCatalog(self):

    index_defs=(('UID', 'FieldIndex'),
                 ('Type', 'FieldIndex'),
                 ('id', 'FieldIndex'),
                 ('Title', 'FieldIndex'),
                 ('portal_type', 'FieldIndex'),
             )

    if not hasattr(self, UID_MANAGER):
        #Add a zcatalog for uids
        addCatalog = manage_addZCatalog
        addCatalog(self, UID_MANAGER, 'UID Catalog')

    catalog = getToolByName(self, UID_MANAGER)
    schema = catalog.schema()
    indexes = catalog.indexes()
    schemaFields = []


    for indexName, indexType in index_defs:

        try:
            if indexName not in indexes:
                catalog.addIndex(indexName, indexType, extra=None)
            if not indexName in schema:
                catalog.addColumn(indexName)
                schemaFields.append(indexName)
        except:
            pass

    catalog.manage_reindexIndex(ids=schemaFields)

def install_referenceCatalog(self):
    index_defs = ( ('sourceUID', 'FieldIndex'),
                   ('targetUID', 'FieldIndex'),
                   ('relationship', 'FieldIndex'),
                   ('targetId', 'FieldIndex'),
                   ('targetTitle', 'FieldIndex'),
                   )
    
    if not hasattr(self, REFERENCE_MANAGER):
        #Add a zcatalog for uids
        addCatalog = manage_addReferenceCatalog
        addCatalog(self, REFERENCE_MANAGER, 'Reference Catalog')
        catalog = getToolByName(self, REFERENCE_MANAGER)
        schema = catalog.schema()
        for indexName, indexType in index_defs:
            try:
                catalog.addIndex(indexName, indexType, extra=None)
            except:
                pass
            try:
                if not indexName in schema:
                    catalog.addColumn(indexName)
            except:
                pass



