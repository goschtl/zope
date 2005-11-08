from OFS.Folder import Folder

def initialize(context):
    from OFS.misc_ import Misc_
    from OFS.Folder import Folder
    from OFS.Application import Application
    from Products.ExternalEditor.__init__ import methods
    from Products.ExternalEditor.__init__ import misc_
    for methodname in methods:
        if not hasattr(Folder, methodname):
            setattr(Folder, methodname, methods[methodname])
    misc = Misc_('ExternalEditor', misc_)
    Application.misc_.__dict__['ExternalEditor'] = misc
    

