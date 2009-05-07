import os, time, glob
from datetime import datetime
from zope.interface import implements
from zope import component
from hurry.custom.interfaces import NotSupported
from hurry.custom.interfaces import (
    ITemplate, IManagedTemplate, ITemplateDatabase, IDataLanguage,
    ISampleExtension)

def register_language(template_class, extension, sample_extension=None):
    component.provideUtility(template_class,
                             provides=ITemplate,
                             name=extension)
    if sample_extension is not None:
        component.provideUtility(sample_extension,
                                 provides=ISampleExtension,
                                 name=extension)

def register_data_language(parse_func, extension):
    component.provideUtility(parse_func,
                             provides=IDataLanguage,
                             name=extension)

def recognized_languages():
    return component.getUtilitiesFor(ITemplate)

def register_collection(id, path, title=None):
    if title is None:
        title = id
    db = FilesystemTemplateDatabase(id=id, path=path, title=title)
    component.provideUtility(db,
                             provides=ITemplateDatabase,
                             name=id)

def lookup(id, template_path):
    db = component.getUtility(ITemplateDatabase, name=id)
    while db.get_source(template_path) is None:
        db = getNextUtility(db, ITemplateDatabase, name=id) 
    dummy, ext = os.path.splitext(template_path)
    template_class = component.getUtility(ITemplate, name=ext)
    return ManagedTemplate(template_class, db, template_path)

def sample_datas(id, template_path):
    db = get_filesystem_database(id)

def structure(id):
    extensions = set([extension for
                      (extension, language) in recognized_languages()])
    db = _get_root_database(id)
    return _get_structure_helper(db.path, db.path, extensions)

class ManagedTemplate(object):
    implements(IManagedTemplate)
    
    def __init__(self, template_class, db, template_path):
        self.template_class = template_class
        self.db = db
        self.template_path = template_path
        self.load()
        self._last_updated = 0
        
    def load(self):
        self.template = self.template_class(
            self.db.get_source(self.template_path))

    def check(self):
        mtime = self.db.get_modification_time(self.template_path)
        if mtime > self._last_updated:
            self._last_updated = mtime
            self.load()

    @property
    def source(self):
        self.check()
        return self.template.source

    @property
    def original_source(self):
        db = queryNextUtility(self.db, ITemplateDatabase,
                              name=self.db.id,
                              default=self.db)
        return db.get_source(self.template_path)

    def __call__(self, input):
        self.check()
        return self.template(input)

    def samples(self):
        db = _get_root_database(self.db.id)
        return db.get_samples(self.template_path)
        
class FilesystemTemplateDatabase(object):
    implements(ITemplateDatabase)

    template_encoding = 'UTF-8'
    
    def __init__(self, id, path, title):
        self.id = id
        self.path = path
        self.title = title
        
    def get_source(self, template_id):
        template_path = os.path.join(self.path, template_id)
        f = open(template_path, 'r')
        result = f.read()
        f.close()
        return unicode(result, self.template_encoding)
    
    def get_modification_time(self, template_id):
        template_path = os.path.join(self.path, template_id)
        return os.path.getmtime(template_path)

    def get_samples(self, template_id):
        template_path = os.path.join(self.path, template_id)
        template_dir = os.path.dirname(template_path)
        template_name, extension = os.path.splitext(template_id)
        result = {}
        sample_extension = component.queryUtility(ISampleExtension,
                                                  name=extension,
                                                  default=None)
        if sample_extension is None:
            return result
        parse = component.getUtility(IDataLanguage, name=sample_extension)
        for path in glob.glob(
            os.path.join(template_dir,
                         template_name + '-*' + sample_extension)):
            filename = os.path.basename(path)
            name, dummy = os.path.splitext(filename)
            # +1 to adjust for -
            name = name[len(template_name) + 1:]        
            f = open(path, 'rb')
            data = f.read()
            f.close()
            result[name] = parse(data)
        return result

    def update(self, template_id, source):
        raise NotSupported(
            "Cannot update templates in FilesystemTemplateDatabase.")

class InMemoryTemplateSource(object):
    def __init__(self, source):
        self.source = source
        self.last_updated = time.time()

class InMemoryTemplateDatabase(object):
    implements(ITemplateDatabase)
    
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self._templates = {}

    def get_source(self, template_id):
        try:
            return self._templates[template_id].source
        except KeyError:
            return None
        
    def get_modification_time(self, template_id):
        try:
            return self._templates[template_id].last_updated
        except KeyError:
            return None

    def get_samples(self, template_id):
        return {}

    def update(self, template_id, source):
        self._templates[template_id] = InMemoryTemplateSource(source)

def _get_structure_helper(path, collection_path, extensions):
    entries = os.listdir(path)
    result = []
    for entry in entries:
        entry_path = os.path.join(path, entry)
        if os.path.isdir(entry_path):
            info = {
                'directory': entry,
                'entries': _get_structure_helper(entry_path,
                                                 collection_path, extensions),
                'path': relpath(entry_path, collection_path),
                }
            result.append(info)
        else:
            name, ext = os.path.splitext(entry)
            if ext not in extensions:
                continue
            info = {
                'template': entry,
                'name': name,
                'extension': ext,
                'path': relpath(entry_path, collection_path),
                }
            result.append(info)
    return result

def _get_root_database(id):
    # assume root database is always a FilesystemTemplateDatabase
    db = component.getUtility(ITemplateDatabase, name=id)
    while not isinstance(db, FilesystemTemplateDatabase):
        db = getNextUtility(db, ITemplateDatabase, name=id)
    return db

# XXX copied from zope.app.component to avoid dependency on it
# note that newer versions of zope.component have this, so
# when the target app depends on that we can switch and
# eliminate this code

from zope.component import getSiteManager

_marker = object()

def queryNextUtility(context, interface, name='', default=None):
    """Query for the next available utility.

    Find the next available utility providing `interface` and having the
    specified name. If no utility was found, return the specified `default`
    value.
    """
    sm = getSiteManager(context)
    bases = sm.__bases__
    for base in bases:
        util = base.queryUtility(interface, name, _marker)
        if util is not _marker:
            return util
    return default

def getNextUtility(context, interface, name=''):
    """Get the next available utility.

    If no utility was found, a `ComponentLookupError` is raised.
    """
    util = queryNextUtility(context, interface, name, _marker)
    if util is _marker:
        raise zope.component.interfaces.ComponentLookupError(
              "No more utilities for %s, '%s' have been found." % (
                  interface, name))
    return util

# XXX this code comes from Python 2.6 - when switching to this
# python version we can import it from os.path and get rid of this code
from os.path import commonprefix, abspath, join, sep, pardir

def relpath(path, start):
    """Return a relative version of a path"""

    if not path:
        raise ValueError("no path specified")

    start_list = abspath(start).split(sep)
    path_list = abspath(path).split(sep)

    # Work out how much of the filepath is shared by start and path.
    i = len(commonprefix([start_list, path_list]))

    rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
    return join(*rel_list)
