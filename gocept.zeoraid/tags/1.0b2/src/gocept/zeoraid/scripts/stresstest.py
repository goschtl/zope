import time
import transaction
from ZEO.ClientStorage import ClientStorage
from ZODB import DB
import ZODB.POSException
import ZEO.zrpc.error
import ZEO.Exceptions
import ZODB.utils


storage = ClientStorage([('127.0.0.1', 8100)],#, ('127.0.0.1', 8201)],
                        storage='1')
db = DB(storage)
conn = db.open()
root = conn.root()

root['x'] = 0

while True:
    root['x'] += 1
    try:
        transaction.commit()
    except (ZODB.POSException.ConflictError,
            ZEO.zrpc.error.DisconnectedError,
            ZEO.Exceptions.ClientDisconnected):
        transaction.abort()
        continue
    print root['x']
    print ZODB.utils.oid_repr(storage.lastTransaction())
    time.sleep(1)
