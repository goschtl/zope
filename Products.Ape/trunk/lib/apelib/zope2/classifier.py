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
"""Zope 2 object classification.

$Id$
"""

from mimetypes import guess_extension

from Acquisition import aq_base

from apelib.core.interfaces import IConfigurableClassifier
from apelib.core.interfaces import ClassificationError

# guess_extension() is useful, but it's unoptimized and sometimes
# chooses strange extensions.  fixed_extensions does nothing other than
# suggest a filename extension given a content type.  It contains
# some better defaults.
fixed_extensions = {
    'text/plain': '.txt',
    'text/html':  '.html',
    'image/png':  '.png',
    'image/jpg':  '.jpg',
    'image/jpeg': '.jpg',
    'image/gif':  '.gif',
    'application/octet-stream': '',  # No extension--too overloaded.
    }

generic_classifications = ('directory', 'file', 'basepath')


class Classifier:
    """A classifier with some minimal Zope 2 extensions.
    """
    __implements__ = IConfigurableClassifier
    gateway = None

    def __init__(self, gw=None):
        self.gateway = gw
        self.store_map = {}  # { class_name -> { mapper name, other options } }
        self.load_alias_map = {}  # { old mapper name -> new mapper name }
        self.load_ext_map = {}  # { '.ext' -> mapper name }
        self.load_generic_map = {}  # { keyword -> mapper name }

    def add_store_rule(self, class_name, mapper_name, exact=False,
                       default_extension=None, default_extension_source=None):
        self.store_map[class_name] = {
            'mapper_name': mapper_name,
            'exact': exact,
            'default_extension': default_extension,
            'default_extension_source': default_extension_source,
            }

    def add_load_rule(self, criterion, value, mapper_name):
        value = str(value)  # Avoid unicode
        if criterion == 'mapper-name':
            self.load_alias_map[value] = mapper_name
        elif criterion == 'extension':
            self.load_ext_map[value] = mapper_name
        elif criterion == 'generic':
            self.load_generic_map[value] = mapper_name
        else:
            raise ValueError('Unknown classification criterion: %s'
                             % repr(criterion))


    def find_class_mapper(self, event, klass, is_base=False):
        """Searches for a mapper of a given class, including base classes.

        Returns a value in store_map or None.
        """
        try:
            class_name = '%s.%s' % (klass.__module__, klass.__name__)
        except AttributeError:
            return None
        d = self.store_map.get(class_name)
        if d is not None:
            if is_base and d.get('exact'):
                # this rule doesn't want subclasses.
                d = None
        if d is None:
            for base in klass.__bases__:
                d = self.find_class_mapper(event, base, is_base=True)
                if d is not None:
                    break
        return d


    def classify_object(self, event):
        """Chooses a classification, including a mapper, for storing an object.
        """
        if event.oid == event.conf.oid_gen.root_oid:
            # Use the root mapper if one is configured.
            mapper_name = self.load_generic_map.get('root')
            if mapper_name is not None:
                return {'mapper_name': mapper_name}
        klass = event.obj.__class__
        class_name = '%s.%s' % (klass.__module__, klass.__name__)
        classification = {'class_name': class_name}
        opts = self.find_class_mapper(event, klass)
        if opts is None:
            raise ClassificationError(
                'No mapper known for class %s' % repr(class_name))
        classification['mapper_name'] = opts['mapper_name']
        if opts.get('default_extension_source') == 'content_type':
            ct = str(getattr(aq_base(event.obj), 'content_type', None))
            ext = fixed_extensions.get(ct)
            if ext is None:
                ext = guess_extension(ct)
        else:
            ext = opts.get('default_extension')
        if ext:
            classification['extension'] = ext
        return classification


    def classify_state(self, event):
        """Chooses a classification, including a mapper, for loading an object.
        """
        if event.oid == event.conf.oid_gen.root_oid:
            # Use the root mapper if one is configured.
            mapper_name = self.load_generic_map.get('root')
            if mapper_name is not None:
                return {'mapper_name': mapper_name}
        classification, serial = self.gateway.load(event)
        class_name = classification.get('class_name')
        if class_name and ':' in class_name:
            # Backward compatibility
            class_name = class_name.replace(':', '.')
            classification['class_name'] = class_name
        mapper_name = classification.get('mapper_name')
        if mapper_name is not None:
            # Possibly update to a new mapper name
            mapper_name = self.load_alias_map.get(
                mapper_name, mapper_name)
        if mapper_name is None:
            # The choice of mapper is not stored explicitly.  Choose
            # one based on several criteria.
            if False:
                # bw compat: look for certain meta_types.
                mt = classification.get('meta_type')
                if mt == '(folderish object)':
                    mapper_name = 'anyfolder'
                elif mt == '(fileish object)':
                    mapper_name = 'anyfile'
            if mapper_name is None:
                subpath = classification.get('subpath')
                if subpath is not None and not subpath:
                    # Application base
                    mapper_name = self.load_generic_map.get('basepath')
            if mapper_name is None:
                t = classification.get('node_type')
                if t == 'd':
                    # Directory
                    mapper_name = self.load_generic_map.get('directory')
                elif t == 'f':
                    # File
                    ext = classification.get('extension')
                    if ext:
                        if not ext.startswith('.'):
                            ext = '.' + ext
                        mapper_name = self.load_ext_map.get(ext.lower())
                    if not mapper_name:
                        mapper_name = self.load_generic_map.get('file')
        if mapper_name is None:
            raise ClassificationError(
                'No mapper known for oid %s' % repr(event.oid))

        classification['mapper_name'] = mapper_name
        return classification
