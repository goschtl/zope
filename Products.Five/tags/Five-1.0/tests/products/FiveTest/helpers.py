import urllib

def add_and_edit(self, id, REQUEST):
    """Helper function to point to the object's management screen if
    'Add and Edit' button is pressed.
    id -- id of the object we just added
    """
    if REQUEST is None:
        return
    try:
        u = self.DestinationURL()
    except:
        u = REQUEST['URL1']
    if REQUEST.has_key('submit_edit'):
        u = "%s/%s" % (u, urllib.quote(id))
    REQUEST.RESPONSE.redirect(u+'/manage_main')


from OFS.Folder import Folder

class NoVerifyPasteFolder(Folder):
    """Folder that does not perform paste verification.
    Used by test_events
    """
    def _verifyObjectPaste(self, object, validate_src=1):
        pass

def manage_addNoVerifyPasteFolder(container, id, title=''):
    container._setObject(id, NoVerifyPasteFolder())
    folder = container[id]
    folder.id = id
    folder.title = title

class FiveTraversableFolder(Folder):
    """Folder that is declared Five traversable, see configure.zcml
    """
    pass

def manage_addFiveTraversableFolder(container, id, title=''):
    container._setObject(id, FiveTraversableFolder())
    folder = container[id]
    folder.id = id
    folder.title = title

