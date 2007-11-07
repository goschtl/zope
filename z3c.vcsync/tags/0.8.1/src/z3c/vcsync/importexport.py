import py
import tempfile, zipfile

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

def export_state_zip(state, name, zippath):
    tmp_dir = py.path.local(tempfile.mkdtemp())
    try:
        save_path = tmp_dir.join(name)
        save_path.ensure(dir=True)
        export_state(state, save_path)
        zf = zipfile.ZipFile(zippath.strpath, 'w')
        export_state_zip_helper(zf, tmp_dir, save_path)
        zf.close()
    finally:
        tmp_dir.remove()
    
def export_state_zip_helper(zf, save_path, path):
    if path.check(dir=True):
        zf.writestr(path.relto(save_path) + '/', '')
        for p in path.listdir():
            export_state_zip_helper(zf, save_path, p)
    else:
        zf.write(path.strpath, path.relto(save_path))

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

def import_state_zip(state, name, zippath):
    tmp_dir = py.path.local(tempfile.mkdtemp())
    try:
        zf = zipfile.ZipFile(zippath.strpath, 'r')
        for p in zf.namelist():
            if p.endswith('/'):
                p = p[:-1]
                dir = True
            else:
                dir = False
            new_path = tmp_dir.join(*p.split('/'))
            if not dir:
                new_path.ensure()
                new_path.write(zf.read(p))
            else:
                new_path.ensure(dir=True)
        import_state(state, tmp_dir.join(name))
        zf.close()
    finally:
        tmp_dir.remove()
