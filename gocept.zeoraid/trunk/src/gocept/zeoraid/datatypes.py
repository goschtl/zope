import ZODB.config
import gocept.zeoraid.storage

class Storage(ZODB.config.BaseConfig):

    def open(self):
        # Ensure that compatibility is set up.
        gocept.zeoraid.compatibility.setup()
        return gocept.zeoraid.storage.RAIDStorage(self.name,
                                                  self.config.storages)
