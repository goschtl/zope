
"""
ZSQLAlchemy

$Id$
"""

from Globals import InitializeClass
from Shared.DC.ZRDB.TM import TM
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

import sqlalchemy
import psycopg2 as psycopg

psycopg = sqlalchemy.pool.manage(psycopg)


class SessionProxy(object, TM):

    security = ClassSecurityInfo()

    def __init__(self, engine):
        self._engine = engine
        self._session = sqlalchemy.create_session(bind_to=engine)
        self._register()  # register with TM

    def _finish(self):
        """ commit transaction """

        if self._session is None:
            raise RuntimeError('_session is None. This should not happen :-)')

        self._session.flush()
        self._session = None

    def _abort(self):
        """ abort transaction """
        # Nothing to do here since SQLAlchemy starts the transaction with the
        # current session only when calling its flush() method


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

    security.declarePrivate('_getConnection')
    def _getConnection(self):
        """ connection factory """

        db = psycopg.connect(database=self.database, 
                             user=self.username,
                             password=self.password,
                             host=self.hostname)
        return db


    security.declarePrivate('_getEngine')
    def _getEngine(self):
        """ create an engine """

        engine = getattr(self, '_v_sqlalchemy_engine', None)
        if engine is None:
            p = sqlalchemy.pool.QueuePool(self._getConnection, 
                                          max_overflow=10, 
                                          pool_size=10, 
                                          use_threadlocal=True)
            engine = sqlalchemy.create_engine('postgres://', pool=p)
            self._v_sqlalchemy_engine = engine

        return engine


    security.declarePublic('getSession')
    def getSession(self):
        """ return a session proxy """

        engine = self._getEngine()
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
