from zope.app.container.interfaces import IContainer
from z3c.vcsync.interfaces import IVcDump, IVcFactory
from zope.component import getUtility

def export_state(state, path):
    export_helper(state.root, path)
    
def export_helper(obj, path):
    for obj in obj.values():
        IVcDump(obj).save(path)
        if IContainer.providedBy(obj):
            export_helper(obj, path.join(obj.__name__))

def import_state(state, path):
    import_helper(state.root, path)

def import_helper(obj, path):
    for p in path.listdir():
        factory = getUtility(IVcFactory, name=p.ext)
        name = p.purebasename
        if name in obj:
            del obj[name]
        obj[name] = new_obj = factory(p)
        if p.check(dir=True):
            import_helper(new_obj, p)
