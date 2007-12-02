import ZODB.config
import zc.virtualstorage.base

class Database(ZODB.config.BaseConfig):

    def open(self, databases=None):
        section = self.config
        storage = section.storage.open()
        try:
            return zc.virtualstorage.base.DB(storage,
                           pool_size=section.pool_size,
                           cache_size=section.cache_size,
                           historical_pool_size=section.historical_pool_size,
                           historical_cache_size=section.historical_cache_size,
                           historical_timeout=section.historical_timeout,
                           database_name=section.database_name,
                           databases=databases,
                           virtual_pool_size=section.virtual_pool_size,
                           virtual_cache_size=section.virtual_cache_size,
                           virtual_timeout=section.virtual_timeout,
                           )
        except:
            storage.close()
            raise