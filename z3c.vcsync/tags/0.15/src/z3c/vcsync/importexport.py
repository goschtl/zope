import py
import tempfile, zipfile

from zope.app.container.interfaces import IContainer
from z3c.vcsync.interfaces import IDump, IFactory
from zope.component import getUtility
    
def export(root, path):
    for obj in root.values():
        IDump(obj).save(path)
        if IContainer.providedBy(obj):
            export(obj, path.join(obj.__name__))

def export_zip(root, name, zippath):
    tmp_dir = py.path.local(tempfile.mkdtemp())
    try:
        save_path = tmp_dir.join(name)
        save_path.ensure(dir=True)
        export(root, save_path)
        zf = zipfile.ZipFile(zippath.strpath, 'w')
        _export_zip_helper(zf, tmp_dir, save_path)
        zf.close()
    finally:
        tmp_dir.remove()
    
def _export_zip_helper(zf, save_path, path):
    if path.check(dir=True):
        zf.writestr(path.relto(save_path) + '/', '')
        for p in path.listdir():
            _export_zip_helper(zf, save_path, p)
    else:
        zf.write(path.strpath, path.relto(save_path))

def import_(root, path, modified_function=None):
    modified_objects = _import_helper(root, path)
    if modified_function is not None:
        for obj in modified_objects:
            modified_function(obj)

def _import_helper(obj, path):
    modified_objects = []
    for p in path.listdir():
        factory = getUtility(IFactory, name=p.ext)
        name = p.purebasename
        if name not in obj:
            obj[name] = new_obj = factory(p)
            modified_objects.append(new_obj)
        else:
            new_obj = obj[name]
        if p.check(dir=True) and IContainer.providedBy(new_obj):
            r = _import_helper(new_obj, p)
            modified_objects.extend(r)
    return modified_objects

def import_zip(root, name, zippath, modified_function=None):
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
        import_(root, tmp_dir.join(name),
                modified_function=modified_function)
        zf.close()
    finally:
        tmp_dir.remove()
