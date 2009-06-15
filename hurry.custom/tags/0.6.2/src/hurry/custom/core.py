import os, time, glob
from datetime import datetime
from zope.interface import implements
from zope import component
from zope.component.interfaces import ComponentLookupError
from hurry.custom.interfaces import (
    ITemplate, IManagedTemplate, ITemplateDatabase, IDataLanguage,
    ISampleExtension, CompileError, RenderError, NotSupported)

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

def render(id, template_path, input):
    template = lookup(id, template_path)
    while True:
        try:
            return template(input)
        except RenderError, render_error:
            try:
                next_db = next_collection(id, template.db)
            except ComponentLookupError:
                # cannot find any next collection, so this error is it
                raise render_error
            template = lookup(id, template_path, db=next_db)

def lookup(id, template_path, db=None):
    dummy, ext = os.path.splitext(template_path)
    template_class = component.getUtility(ITemplate, name=ext)

    db = db or collection(id)

    while True:
        source = db.get_source(template_path)
        if source is not None:
            try:
                return ManagedTemplate(template_class, db, template_path)
            except CompileError, e:
                pass
        try:
            db = next_collection(id, db)
        except ComponentLookupError:
            # if we cannot find a next collection, this means the
            # last collection had a fatal compilation error
            raise e

def collection(id):
    return component.getUtility(ITemplateDatabase, name=id)

def next_collection(id, db):
    result = getNextUtility(db, ITemplateDatabase, name=id)
    if result is db:
        raise ComponentLookupError("No collection available for: %s" % id)
    return result

def root_collection(id):
    db = collection(id)
    while True:
        try:
            next_db = next_collection(id, db)
        except ComponentLookupError:
            return db
        db = next_db

def check(id, template_path, source):
    dummy, ext = os.path.splitext(template_path)
    template_class = component.getUtility(ITemplate, name=ext)
    # can raise CompileError
    template = template_class(source)
    db = root_collection(id)
    samples = db.get_samples(template_path)
    for key, value in samples.items():
        try:
            template(value)
        except RenderError, e:
            # add data_id and re-raise
            e.data_id = key
            raise e

def structure(id):
    extensions = set([extension for
                      (extension, language) in recognized_languages()])
    db = root_collection(id)
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

    def __call__(self, input):
        self.check()
        return self.template(input)
    
class FilesystemTemplateDatabase(object):
    implements(ITemplateDatabase)

    template_encoding = 'UTF-8'
    
    def __init__(self, id, path, title):
        self.id = id
        self.path = path
        self.title = title

    def update(self, template_id, source):
        raise NotSupported(
            "Cannot update templates in FilesystemTemplateDatabase.")

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
        try:
            parse = component.getUtility(IDataLanguage, name=sample_extension)
        except ComponentLookupError:
            return result
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

    def update(self, template_id, source):
        self._templates[template_id] = InMemoryTemplateSource(source)

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

def _get_structure_helper(path, collection_path, extensions):
    entries = os.listdir(path)
    result = []
    for entry in entries:
        if entry.startswith('.'):
            continue
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
        raise ComponentLookupError(
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
