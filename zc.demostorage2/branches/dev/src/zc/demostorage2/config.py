
import demostorage2
from ZODB.config import BaseConfig

class DemoStorage2(BaseConfig):

    def open(self):
        base = self.config.base.open()
        changes = self.config.changes.open()
        return demostorage2.DemoStorage2(base, changes)
