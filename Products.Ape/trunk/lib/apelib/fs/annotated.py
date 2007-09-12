##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""AnnotatedFilesystem class.

$Id$
"""

import re
from time import time
from types import StringType


# This expression matches "\n[sectionname]...\n", where len(sectionname) > 0.
section_re = re.compile(r'^\[([^\[\]\n]+)\][^\r\n]*(?:\r\n|\r|\n)',
                      re.MULTILINE)

properties_ext = 'properties'
remainder_ext = 'remainder'

# Match 'foo.properties', 'foo.remainder', 'properties', or 'remainder'.
# This is for filtering out annotation filenames.
annotation_re = re.compile('(|.+[.])(%s|%s)$' % (
    properties_ext, remainder_ext))

# Names of annotations handled by this module
remainder_ann = 'remainder'         # The value is a binary string.
object_names_ann = 'object_names'


class AnnotatedFilesystem:
    """Filesystem abstraction that adds annotations and automatic extensions.

    Annotations are stored in .properties files.
    """

    def __init__(self, ops, annotation_prefix='.', hidden_filenames='_'):
        self.ops = ops
        self.annotation_prefix = annotation_prefix
        self.hidden_re = re.compile(hidden_filenames)
        # _anns_cache: { path -> annotations }
        self._anns_cache = ShortLivedCache()
        # _dir_cache: { path -> directory info }
        self._dir_cache = ShortLivedCache()

    def clear_cache(self):
        """Clears the cache of annotations and automatic filename extensions.

        Useful after writing to the filesystem.
        """
        self._anns_cache.clear()
        self._dir_cache.clear()

    def invalidate(self, path):
        """Invalidates info about a path being written.
        """
        self._anns_cache.invalidate(path)
        self._dir_cache.invalidate(path)

    def get_annotation_paths(self, path):
        """Returns the property and remainder paths for a path.
        """
        ops = self.ops
        if ops.isdir(path):
            base_fn = ops.join(path, self.annotation_prefix)
        else:
            dirname, filename = ops.split(path)
            base_fn = ops.join(dirname, '%s%s.' % (
                self.annotation_prefix, filename))
        return (base_fn + properties_ext, base_fn + remainder_ext)

    def get_annotations(self, path):
        """Reads the annotations for a path."""
        res = self._anns_cache.get(path)
        if res is not None:
            return res
        props_fn, rem_fn = self.get_annotation_paths(path)
        res = {}
        try:
            data = self.ops.readfile(rem_fn, 0)
        except IOError:
            # The remainder file does not exist.
            pass
        else:
            res[remainder_ann] = data
            # Note properties file can override the remainder.
        try:
            data = self.ops.readfile(props_fn, 1)
        except IOError:
            # The properties file apparently does not exist
            self._anns_cache.set(path, res)
            return res
        pos = 0
        prev_section_name = None
        while 1:
            match = section_re.search(data, pos)
            if match is None:
                endpos = len(data)
            else:
                endpos = match.start()
            if prev_section_name is not None:
                # get the data and decode.
                section = data[pos:endpos].replace('[[', '[')
                res[prev_section_name] = section
            if match is None:
                break
            else:
                prev_section_name = match.group(1)
                pos = match.end()
        self._anns_cache.set(path, res)
        return res

    def check_annotation_name(self, ann_name):
        if (not isinstance(ann_name, StringType)
            or not ann_name
            or '[' in ann_name
            or ']' in ann_name
            or '\n' in ann_name):
            raise ValueError(ann_name)

    def write_annotations(self, path, anns):
        props_fn, rem_fn = self.get_annotation_paths(path)
        props_data = ''
        rem_data = ''
        items = anns.items()
        items.sort()
        for name, value in items:
            # Write a section of the properties file.
            props_data += self._format_section(name, value)
        self._write_or_remove(props_fn, 1, props_data)
        self._write_or_remove(rem_fn, 0, rem_data)
        self._anns_cache.invalidate(path)
        # The file might be new, so invalidate the directory.
        self._dir_cache.invalidate(self.ops.dirname(path))

    def _format_section(self, name, text):
        s = '[%s]\n%s\n' % (name, text.replace('[', '[['))
        if not text.endswith('\n'):
            s += '\n'
        return s

    def _write_or_remove(self, fn, as_text, data):
        """If data is provided, write it.  Otherwise remove the file.
        """
        ops = self.ops
        if data:
            ops.writefile(fn, as_text, data)
        else:
            if ops.exists(fn):
                ops.remove(fn)

    def is_legal_filename(self, fn):
        ap = self.annotation_prefix
        if (not fn or
            (fn.startswith(ap) and annotation_re.match(fn, len(ap)))
            or self.hidden_re.match(fn) is not None):
            return 0
        return 1

    def compute_contents(self, path, allow_missing=0):
        """Returns the name translations for a directory.  Caches the results.

        Returns ({filename: name}, {name: filename}).
        """
        res = self._dir_cache.get(path)
        if res is not None:
            return res

        try:
            fns = self.ops.listdir(path)
        except OSError:
            if allow_missing:
                return {}, {}
            raise
        
        obj_list = []   # [name]
        trans = {}     # { base name -> filename with extension or None }
        filenames = filter(self.is_legal_filename, fns)
        anns = self.get_annotations(path)
        text = anns.get(object_names_ann)
        if text:
            # Prepare a dictionary of translations from basename to filename.
            for fn in filenames:
                if '.' in fn:
                    base, ext = fn.split('.', 1)
                    if trans.has_key(base):
                        # Name collision: two or more files have the same base
                        # name.  Don't strip the extensions for any of them.
                        trans[base] = None
                    else:
                        trans[base] = fn
                else:
                    trans[fn] = None
            obj_list = [line.strip() for line in text.split('\n')]
            for obj_name in obj_list:
                if '.' in obj_name:
                    # An object name uses an extension.  Don't translate
                    # any name that uses the same base name.
                    base, ext = obj_name.split('.', 1)
                    trans[base] = None

        fn_to_name = {}
        for fn in filenames:
            fn_to_name[fn] = fn
        # Translate the file names to object names.
        for obj_name in obj_list:
            fn = trans.get(obj_name)
            if fn:
                fn_to_name[fn] = obj_name
        name_to_fn = {}
        for fn, name in fn_to_name.items():
            name_to_fn[name] = fn
        res = (fn_to_name, name_to_fn)
        self._dir_cache.set(path, res)
        return res


class ShortLivedCache:
    """Simple short-lived object cache.
    """
    def __init__(self, lifetime=1):
        # The default lifetime is 1 second.
        self.lifetime = lifetime
        self.data = {}
        self.expiration = time() + lifetime

    def get(self, key, default=None):
        now = time()
        if now >= self.expiration:
            self.data.clear()
            return default
        res = self.data.get(key, default)
        return res

    def set(self, key, value):
        now = time()
        if now >= self.expiration:
            self.data.clear()
            self.expiration = now + self.lifetime
        self.data[key] = value

    def invalidate(self, key):
        try:
            del self.data[key]
        except KeyError:
            pass

    def clear(self):
        self.data.clear()
