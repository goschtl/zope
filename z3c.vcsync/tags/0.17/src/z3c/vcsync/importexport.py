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
    zf = zipfile.ZipFile(zippath.strpath, 'w')
    zf.writestr('data/', '')
    _export_zip_helper(root, zf, 'data')
    zf.close()
    
def _export_zip_helper(root, zf, save_path):
    for obj in root.values():
        name, bytes = IDump(obj).save_bytes()
        if save_path:
            sub_path = save_path + '/' + name
        else:
            sub_path = name
        sub_path = sub_path.encode('cp437')
        if IContainer.providedBy(obj):
            # create a directory 
            zf.writestr(sub_path + '/', '')
            _export_zip_helper(obj, zf, sub_path)
        else:
            zf.writestr(sub_path, bytes)
        
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
