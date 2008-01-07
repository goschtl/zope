
# Helper method to make ZEO play nice. IMHO ZEO does not implement the
# interface correctly.
def _zeoraid_lastTransaction(self):
    return self._server.lastTransaction()

import ZEO.ClientStorage
ZEO.ClientStorage.ClientStorage._zeoraid_lastTransaction = _zeoraid_lastTransaction
