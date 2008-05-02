import grok

from collective.lead import Database as DatabaseBase
from collective.lead.interfaces import IDatabase

from megrok.rdb.components import Model
from megrok.rdb.interfaces import IDatabase as IRdbDatabase

class Database(grok.GlobalUtility, DatabaseBase):
    grok.implements(IRdbDatabase)
    grok.provides(IDatabase)
    grok.name('megrok.rdb')
    grok.baseclass()

    @property
    def _url(self):
        # XXXX missing 'url' gets turned into an AttributeError for `_url`
        # instead of `url`, which sucks.
        return self.url
    
    def _setup_tables(self, metadata, tables):
        self.metadata = metadata = Model.metadata
        Model.metadata.create_all(self._engine)
        self.setup(metadata)

    def setup(self, metadata):
        pass
