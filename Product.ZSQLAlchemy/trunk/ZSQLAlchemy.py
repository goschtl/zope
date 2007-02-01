
"""
ZSQLAlchemy

$Id: TextIndexNG3.py 1754 2007-01-27 10:38:25Z ajung $
"""

from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile


import sqlalchemy
import psycopg2 as psycopg

psycopg = sqlalchemy.pool.manage(psycopg)


class SessionProxy(object):

    security = ClassSecurityInfo()

    def __init__(self, engine):
        self._engine = engine


    security.declarePublic('getEngine')
    def getEngine(self):
        """ return the engine """
        return self._engine


    security.declarePublic('getMetaData')
    def getMetaData(self):      
        """ return a MetaData instance """
        return sqlalchemy.BoundMetaData(self._engine)


InitializeClass(SessionProxy)



class ZSQLAlchemy(SimpleItem, PropertyManager):

    meta_type = 'ZSQLAlchemy'
    hostname = ''
    username = ''
    password = ''
    database = ''

    manage_options = SimpleItem.manage_options + \
                     PropertyManager.manage_options    

    _properties=(
                 {'id':'hostname', 'type':'string', 'mode':'wrd'},
                 {'id':'username', 'type':'string', 'mode':'wrd'},
                 {'id':'password', 'type':'string', 'mode':'wrd'},
                 {'id':'database', 'type':'string', 'mode':'wrd'},
                 )

    security = ClassSecurityInfo()

    def _getConnection(self):
        """ connection factory """
        db = psycopg.connect(database=self.database, 
                             user=self.username,
                             password=self.password,
                             host=self.hostname)

        return db


    def _createEngine(self):
        """ create an engine """
        
        p = sqlalchemy.pool.QueuePool(self._getConnection, max_overflow=10, pool_size=10, use_threadlocal=True)
        engine = sqlalchemy.create_engine('postgres://', pool=p)
        return engine


    security.declarePublic('getSession')
    def getSession(self):
        """ return a session proxy """

        engine = self._createEngine()
        proxy = SessionProxy(engine)
        return proxy


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
