
"""
ZSQLAlchemy

$Id: TextIndexNG3.py 1754 2007-01-27 10:38:25Z ajung $
"""

from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

class ZSQLAlchemy(SimpleItem, PropertyManager):

    meta_type = 'ZSQLAlchemy'
    connection_url = ''

    manage_options = SimpleItem.manage_options + \
                     PropertyManager.manage_options    

    _properties=({'id':'connection_url',
                  'type':'string',
                  'mode':'wrd'},)

    security = ClassSecurityInfo()


InitializeClass(ZSQLAlchemy)


manage_addZSQLAlchemyForm = PageTemplateFile( "pt/add.pt", globals(), __name__ = 'manage_addZSQLAlchemyForm')

def manage_addZSQLAlchemy(self, id, REQUEST=None):
    """ """

    zs = ZSQLAlchemy(id)
    self._setObject(id, zs)

    if REQUEST:
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_workspace')
    else:
        return zs
