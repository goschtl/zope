from zope import interface

import threading
import interfaces
import time
import xappy

class ConnectionHub(object):
    interface.implements(interfaces.IConnectionHub)
    
    auto_refresh_delta = 20 # max time in seconds till we refresh a connection

    def __init__(self, index_path):
        self.store = threading.local()
        self.modified = time.time()
        self.index_path = index_path
        
    def invalidate(self):
        self.modified = time.time()

    def get(self):
        conn = getattr(self.store, 'connection', None)
        
        now = time.time()
        if self.modified + self.auto_refresh_delta < now:
            self.modified = now
        
        if conn is None:
            self.store.connection = conn = xappy.SearchConnection(self.index_path)
            self.store.opened = now
                
        opened = getattr(self.store, 'opened')
        
        if opened < self.modified:
            conn.reopen()            
            self.store.opened = now
            
        return conn
