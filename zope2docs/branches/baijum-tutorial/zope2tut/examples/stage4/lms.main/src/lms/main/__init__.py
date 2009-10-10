from OFS.Folder import Folder

def addLmsMain(dispatcher, id="lms"):
    """Add LMS"""
    dispatcher._setObject(id, LmsMain(id))
    return "LMS Installed: %s" % id

class LmsMain(Folder):
    meta_type = "LMS"

def initialize(registrar):
    registrar.registerClass(LmsMain,
                            constructors=(addLmsMain,))
