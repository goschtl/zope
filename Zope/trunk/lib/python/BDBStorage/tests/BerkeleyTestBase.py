# Basic test framework class for both the Full and Minimal Berkeley storages

import os
from StorageTestBase import StorageTestBase

DBHOME = 'test-db'



class BerkeleyTestBase(StorageTestBase):
    def setUp(self):
        StorageTestBase.setUp(self)
        os.mkdir(DBHOME)
        try:
            self._storage = self.ConcreteStorage(DBHOME)
        except:
            self.tearDown()
            raise

    def tearDown(self):
        # If the tests exited with any uncommitted objects, they'll blow up
        # subsequent tests because the next transaction commit will try to
        # commit those object.  But they're tied to closed databases, so
        # that's broken.  Aborting the transaction now saves us the headache.
        StorageTestBase.tearDown(self)
        for file in os.listdir(DBHOME):
            os.unlink(os.path.join(DBHOME, file))
        os.removedirs(DBHOME)



class MinimalTestBase(BerkeleyTestBase):
    import Minimal
    ConcreteStorage = Minimal.Minimal


class FullTestBase(BerkeleyTestBase):
    import Full
    ConcreteStorage = Full.Full
