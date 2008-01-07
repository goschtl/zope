import ZODB.config
import gocept.zeoraid.storage

class Storage(ZODB.config.BaseConfig):

    def open(self):
        return gocept.zeoraid.storage.RAIDStorage(self.name,
                                                  self.config.storages)
