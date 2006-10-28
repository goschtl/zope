# -*- coding: UTF-8 -*-

#plugin for ZODB FileStorage data source

import transaction
from ZODB import FileStorage, DB

from wax import *
from z3c.zodbbrowser.bases import BaseSourcePlugin

class ZODBFSPlugin(BaseSourcePlugin):
    storage = None
    db = None
    connection = None
    root = None
    filename = ""
    
    def open_direct(self, Path):
        """Open ZODB.
    
        Returns a tuple consisting of:(root,connection,db,storage)
        The same tuple must be passed to close_zodb() in order to close the DB.
        """
        # Connect to DB
        self.storage     = FileStorage.FileStorage(Path)
        self.db          = DB(self.storage)
        self.connection  = self.db.open()
        self.root        = self.connection.root()
        
        return True
    
    def open(self, parent):
        dlg = FileDialog(parent, open=1)
        try:
            result = dlg.ShowModal()
            if result == 'ok':
                self.filename = dlg.GetPaths()[0]
                return self.open_direct(self.filename)
        finally:
            dlg.Destroy()
        
        return False

    def close(self):
        """Closes the ZODB.
    
        This function MUST be called at the end of each program !!!
        """
        print "closed"
        
        transaction.abort()
        
        self.connection.close()
        self.db.close()
        self.storage.close()
        self.filename = ""
        
        return True
    
    def getSupportedDisplays(self):
        return ['tree']
    
    def getDataForDisplay(self, mode):
        return self.root
    
    def getTitle(self):
        return self.filename

def main(PluginRegistry):
    PluginRegistry['source'].extend([
        ('FileStorage','fs',ZODBFSPlugin)])