from datetime import datetime

import grok

from gbepastebin.store import volatile_pastebin, pastebin

class Application(grok.Application, grok.Container):
    
    display_limit=10
    version=0.1
    
    def next_id(self):
        keys=[0]
        keylist=self.store.keys()
        if keylist:
            keys=[int(key) for key in keylist]
        keys.sort()
        return str(int(keys[-1])+1)

    def get_paste(self, pasteid):
        return self.store.get(pasteid)
    
    def add_paste(self, paste):
        pasteid=self.next_id()
        paste.pasteid=pasteid
        self.store[pasteid]=paste
        return pasteid
    
    def delete_paste(self, pasteid):
        if self.get_paste(pasteid):
            del self.store[pasteid]
            return True
        return False
        
    def list_pastes(self, max=display_limit):
        keylist=self.store.keys()
        keys=[int(key) for key in keylist]
        keys.sort()
        keys.reverse()
        return [self.get_paste(str(key)) for key in keys[:max]]
    
    def list_pasteids(self):
        return list(self.store.keys())
        
    def delete_pastes(self, pastelist):
        success=True
        for pasteid in pastelist:
            delete = self.delete_paste(pasteid)
            success=success and delete
        return success

@grok.subscribe(Application, grok.IObjectAddedEvent)
def handle(obj, event):
    #obj.store=volatile_pastebin()
    obj.store=pastebin()
