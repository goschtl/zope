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
"""Filesystem connection class.

$Id$
"""

import os

from apelib.core.interfaces import ITPCConnection, ISourceRepository, LoadError

from interfaces import IFSReader, IFSWriter, FSReadError, FSWriteError
from fileops import StandardFileOperations
from annotated import AnnotatedFilesystem, object_names_ann
from oidtable import OIDTable

DEBUG = os.environ.get('APE_DEBUG_FS')


# For a node_type_ann, the value is 'f' (file) or 'd' (directory)
node_type_ann = '@node_type'

# data_ann holds the content of a file.  It is not valid for directories.
data_ann = '@data'

# file_list_ann holds the content of a directory.  It is not valid for files.
file_list_ann = '@files'

# The suggested filename extension.
suggested_extension_ann = '@s_ext'


class FSConnection:
    """Reads / writes files with annotations.
    """
    __implements__ = IFSReader, IFSWriter, ITPCConnection, ISourceRepository

    basepath = ''
    root_oid = '0'

    # When app_filename is set, FSConnection translates paths, placing
    # the application object at basepath and the root at
    # (basepath)/_root.
    app_filename = 'Application'

    def __init__(self, basepath, annotation_prefix='.', hidden_filenames='_',
                 ops=None):
        # These attributes are used for both reading and writing.
        self.basepath = basepath
        if ops is None:
            ops = StandardFileOperations()
        self.ops = ops
        self.afs = AnnotatedFilesystem(
            ops, annotation_prefix, hidden_filenames)
        self.table = OIDTable()

        # These attributes are used only for writing.
        self._final = 0  # True if second phase of commit.
        # _pending holds the data to be written.
        # _pending: { oid -> { annotation_name -> data } }
        self._pending = {}
        self._script = None  # [(instruction, *args)]
        self._tmp_subpaths = {}  # { oid: subpath }

    def reset(self):
        self._final = 0
        self._pending.clear()
        self.afs.clear_cache()
        self._script = None
        self._tmp_subpaths.clear()

    #
    # IFSReader implementation.
    #

    def get_subpath(self, oid):
        p = self.table.get_path(self.root_oid, oid)
        if p is None:
            return self._tmp_subpaths.get(oid)
        if self.app_filename:
            # Translate paths.
            if p and p[0] == self.app_filename:
                # Place the application object at basepath.
                return p[1:]
            else:
                # Everything else goes in "_root".
                return ['_root'] + p
        else:
            return p

    def get_path(self, oid):
        p = self.get_subpath(oid)
        if p is None:
            raise LoadError(oid)
        return self.ops.join(self.basepath, *p)

    def read_node_type(self, oid):
        path = self.get_path(oid)
        if not self.ops.exists(path):
            raise LoadError("%s does not exist" % path)
        return self.ops.isdir(path) and 'd' or 'f'

    def read_data(self, oid, allow_missing=0, as_text=0):
        # Return a string.
        try:
            path = self.get_path(oid)
            return self.ops.readfile(path, as_text)
        except (LoadError, IOError):
            if allow_missing:
                return None
            raise

    def read_directory(self, oid, allow_missing=0):
        # Return a sequence of (object_name, child_oid).
        path = self.get_path(oid)
        contents = self.afs.compute_contents(path, allow_missing)
        fn_to_name, name_to_fn = contents
        children = self.table.get_children(oid)
        if children is None:
            children = {}
        # Remove vanished children from the OID table.
        for filename, child_oid in children.items():
            if not fn_to_name.has_key(filename):
                self.table.remove(oid, filename)
                # XXX Need to garbage collect descendants.
        # Return the current children.
        return [(objname, children.get(filename))
                for filename, objname in fn_to_name.items()]

    def read_annotation(self, oid, name, default=None):
        path = self.get_path(oid)
        annotations = self.afs.get_annotations(path)
        return annotations.get(name, default)

    def read_object_name(self, oid):
        parents = self.table.get_parents(oid)
        parent_oid, filename = parents[0]
        parent_path = self.get_path(parent_oid)
        contents = self.afs.compute_contents(parent_path)
        fn_to_name, name_to_fn = contents
        return fn_to_name[filename]

    def read_extension(self, oid):
        path = self.get_path(oid)
        stuff, ext = self.ops.splitext(path)
        return ext

    def assign_existing(self, oid, children):
        """See IFSReader.
        """
        dir_path = self.get_path(oid)
        contents = self.afs.compute_contents(dir_path)
        fn_to_name, name_to_fn = contents
        existing = self.table.get_children(oid) or {}
        for name, child_oid in children:
            assert child_oid
            if existing.has_key(name) and existing[name] != child_oid:
                raise FSReadError("assign_existing() doesn't override")
            filename = name_to_fn[name]
            self.table.add(oid, filename, child_oid)

    def read_mod_time(self, oid, default=0):
        """Returns the time an object was last modified.

        Since objects are split into up to three files, this
        implementation returns the modification time of the most
        recently modified of the three.
        """
        path = self.get_path(oid)
        extra = self.afs.get_annotation_paths(path)
        maxtime = -1
        for p in (path,) + tuple(extra):
            try:
                t = self.ops.getmtime(p)
            except OSError:
                pass
            else:
                if t > maxtime:
                    maxtime = t
        if maxtime == -1:
            maxtime = default
        return maxtime

    def _get_paths_mtime(self, paths):
        t = []
        for path in paths:
            try:
                t.append(self.ops.getmtime(path))
            except OSError:
                t.append(None)
        return t

    def get_sources(self, oid):
        path = self.get_path(oid)
        extra = self.afs.get_annotation_paths(path)
        paths = (path,) + tuple(extra)
        t = self._get_paths_mtime(paths)
        return {(self, paths): t}

    #
    # ISourceRepository implementation.
    #

    def poll(self, sources):
        """ISourceRepository implementation.

        Returns the changed items.
        """
        res = {}
        for source, t in sources.items():
            myself, paths = source
            assert myself is self
            new_t = self._get_paths_mtime(paths)
            if t != new_t:
                res[source] = new_t
        return res

    #
    # IFSWriter implementation.
    #
    def _queue(self, oid, name, data):
        """Queues data to be written at commit time.

        'name' is the name of the annotation.
        """
        m = self._pending
        anns = m.get(oid)
        if anns is None:
            anns = {}
            m[oid] = anns
        if anns.has_key(name):
            if anns[name] != data:
                raise FSWriteError(
                    'Conflicting data storage at %s (%s)' %
                    (oid, name))
        else:
            anns[name] = data

    def write_node_type(self, oid, data):
        if data not in ('d', 'f'):
            raise FSWriteError(
                'Node type must be "d" or "f" at %s' % oid)
        self._queue(oid, node_type_ann, data)

    def write_data(self, oid, data, as_text=0):
        if not isinstance(data, type('')):
            raise FSWriteError(
                'Data for a file must be a string at %s' % oid)
        self._queue(oid, data_ann, (data, as_text))

    def write_directory(self, oid, data):
        if isinstance(data, type('')):  # XXX Need a better check
            raise FSWriteError(
                'Data for a directory must be a list or tuple at %s' % oid)
        is_legal_filename = self.afs.is_legal_filename
        for objname, child_oid in data:
            assert child_oid, "%s lacks a child_oid" % repr(objname)
            if not is_legal_filename(objname):
                raise FSWriteError(
                    'Not a legal object name: %s' % repr(objname))
        self._queue(oid, file_list_ann, data)

    def write_annotation(self, oid, name, data):
        self.afs.check_annotation_name(name)
        self._queue(oid, name, data)

    def suggest_extension(self, oid, ext):
        self._queue(oid, suggested_extension_ann, ext)


    def _prepare_container_changes(self, path, data):
        """Prepares the new dictionary of children for a directory.

        Chooses filenames for all of the directory's children.
        Prevents filename collisions involving extensions by enforcing
        the rule that if there is some object named 'foo.*', an object
        named 'foo' may not have an automatic extension.

        'path' is a filesystem path or None.  'data' is a list of
        (objname, child_oid).  Returns {filename: child_oid}.
        """
        if path:
            existing = self.afs.compute_contents(path)[1]
            # existing contains {objname: filename}
        else:
            existing = {}

        reserved = {}  # { object name stripped of extension: 1 }
        for objname, child_oid in data:
            if '.' in objname:
                base, ext = objname.split('.', 1)
                reserved[base] = 1
        new_filenames = {}
        for objname, child_oid in data:
            filename = objname
            if '.' not in filename and not reserved.has_key(objname):
                # This object is eligible for an automatic extension.
                fn = existing.get(objname)
                if fn:
                    # Use the existing filename.
                    filename = fn
                else:
                    anns = self._pending.get(child_oid)
                    if anns:
                        extension = anns.get(suggested_extension_ann)
                        if extension:
                            if not extension.startswith('.'):
                                extension = '.' + extension
                            filename = objname + extension
            new_filenames[objname] = filename

        fn_oid = {}
        for objname, child_oid in data:
            fn_oid[new_filenames[objname]] = child_oid
        return fn_oid


    def _prepare(self):
        """Prepares for transaction commit.

        Does some early checking while it's easy to bail out.  This
        helps avoid exceptions during the second phase of transaction
        commit.
        """
        container_changes = {}  # {oid: {filename: child_oid}}
        for oid, anns in self._pending.items():
            if self.table.get_parents(oid) or oid == self.root_oid:
                # This is an existing object.  It has a path.
                p = self.get_subpath(oid)
                if p is None:
                    raise FSWriteError(
                        "No path known for OID %s" % repr(oid))
                if p:
                    info = self.ops.join(*p)
                    path = self.ops.join(self.basepath, info)
                else:
                    info = '/'
                    path = self.basepath
                if not self.ops.exists(path):
                    path = None
            else:
                # This is a new object.  It does not have a path yet.
                path = None
                info = 'new object: %s' % repr(oid)
            if path and not self.ops.canwrite(path):
                raise FSWriteError(
                    "Can't get write access. %s" % info)

            # type must be provided and must always be either 'd' or 'f'.
            if not anns.has_key(node_type_ann):
                raise FSWriteError(
                    'Node type not specified for %s' % info)
            t = anns[node_type_ann]
            dir = self.ops.dirname(oid)

            if t == 'f':
                # Writing a file
                data, as_text = anns[data_ann]
                if anns.has_key(file_list_ann):
                    raise FSWriteError(
                        "Files can't have directory contents. %s" % info)
                if path and self.ops.isdir(path):
                    raise FSWriteError(
                        "A directory exists where a file is to be written. %s"
                        % info)

            elif t == 'd':
                # Writing a directory
                data = anns[file_list_ann]
                if anns.has_key(data_ann):
                    raise FSWriteError(
                        "Directories can't have file data. %s" % info)
                if path and not self.ops.isdir(path):
                    raise FSWriteError(
                        "A file exists where a directory is to be written. %s"
                        % info)
                fn_oid = self._prepare_container_changes(path, data)
                container_changes[oid] = fn_oid

            else:
                raise FSWriteError('Node type must be "d" or "f". %s' % info)
        self._script = self._generate_script(container_changes)


    def _generate_script(self, container_changes):
        """Generates the script for committing the transaction.

        Returns [(instruction, *args)].
        """
        # container_changes is {oid: {filename: child_oid}}
        # script is [(instruction, *args)]
        script = []
        script.append(("clear_temp",))

        # Compute the number of times each relevant child_oid is to
        # be linked or unlinked.
        # counts is {child_oid: [link_count, unlink_count]}
        counts = {}
        def increment(child_oid, index, counts=counts):
            c = counts.get(child_oid)
            if c is None:
                counts[child_oid] = c = [0, 0]
            c[index] += 1

        for oid, new_children in container_changes.items():
            old_children = self.table.get_children(oid)
            if old_children is None:
                old_children = {}
            for filename, child_oid in new_children.items():
                if old_children.get(filename) == child_oid:
                    continue  # No change.
                # Adding a link
                increment(child_oid, 0)
                if DEBUG:
                    print 'fs: add link %s/%s -> %s' % (
                        oid, filename, child_oid)
            for filename, child_oid in old_children.items():
                if new_children.get(filename) == child_oid:
                    continue  # No change.
                # Removing a link
                increment(child_oid, 1)
                if DEBUG:
                    print 'fs: del link %s/%s -> %s' % (
                        oid, filename, child_oid)

        # Add steps to the script to move objects to a temporary directory,
        # then delete objects.
        to_delete = []  # [oid]
        for child_oid, (links, unlinks) in counts.items():
            if not self.table.get_parents(child_oid):
                # A new object should be added once or not at all.
                if links > 1:
                    raise FSWriteError(
                        "Multiple links to %s" % repr(child_oid))
            else:
                # An existing object should be moved, removed, or left alone.
                if links > 1 or (links > 0 and unlinks < 1):
                    raise FSWriteError(
                        "Multiple links to %s" % repr(child_oid))
                if links > 0:
                    # Moving.
                    script.append(("move_to_temp", child_oid))
                elif unlinks > 0:
                    # Deleting.
                    to_delete.append(child_oid)

        for child_oid in to_delete:
            script.append(("delete", child_oid))
        script.append(("write_all", container_changes))
        if self.app_filename and container_changes.has_key(self.root_oid):
            # Link or unlink the application object.
            root_changes = container_changes[self.root_oid]
            script.append(("link_app", root_changes.has_key(self.app_filename)))
        script.append(("clear_temp",))
        return script

    def _rmrf(self, path):
        """Delete ala 'rm -rf'.

        If it's a file, remove it.  If it's a directory, remove all of it.
        If it doesn't exist, quietly ignore it.
        """
        ops = self.ops
        if ops.exists(path):
            if ops.isdir(path):
                ops.rmtree(path)
            else:
                ops.remove(path)

    def _do_clear_temp(self):
        """Script command: zap the temporary directory.
        """
        ops = self.ops
        path = ops.join(self.basepath, '_tmp')
        self._rmrf(path)
        self._tmp_subpaths.clear()

    def _move_base_contents(self, src, dest):
        """Move the base directory's contents, but not the directory.

        Also leaves behind the _root and _tmp subdirectories.
        """
        ops = self.ops
        if not ops.exists(dest):
            ops.makedirs(dest)
        for fn in ops.listdir(src):
            if fn not in ('_root', '_tmp'):
                ops.rename(ops.join(src, fn), ops.join(dest, fn))

    def _move_item(self, src, dest):
        """Moves a file or directory.

        For files, also moves annotations next to the file.
        """
        ops = self.ops
        parent = ops.dirname(dest)
        if not ops.exists(parent):
            ops.makedirs(parent)
        if not ops.isdir(src):
            # Move the annotation files also.
            extra_src = self.afs.get_annotation_paths(src)
            extra_dest = self.afs.get_annotation_paths(dest)
            for s, d in zip(extra_src, extra_dest):
                if ops.exists(s):
                    ops.rename(s, d)
        ops.rename(src, dest)

    def _do_move_to_temp(self, oid):
        """Script command: move an object to the temporary directory.
        """
        ops = self.ops
        src = self.get_path(oid)
        if src == self.basepath:
            # Move the base by moving most of the contents
            # instead of the actual directory.
            dest_sub = ('_tmp', 'base', 'data')
            dest = ops.join(self.basepath, *dest_sub)
            self._move_base_contents(src, dest)
        else:
            # Move an object.
            dest_sub = ('_tmp', 'oid.%s' % oid, 'data')
            dest = ops.join(self.basepath, *dest_sub)
            self._move_item(src, dest)
        self._tmp_subpaths[oid] = dest_sub
        parents = self.table.get_parents(oid)
        for parent_oid, filename in parents:
            self.table.remove(parent_oid, filename)

    def _restore(self, oid):
        """Moves an object in the temp directory into the object system.
        """
        ops = self.ops
        dest = self.get_path(oid)
        src_sub = self._tmp_subpaths[oid]
        src = ops.join(self.basepath, *src_sub)
        if dest == self.basepath:
            self._move_base_contents(src, dest)
        else:
            self._move_item(src, dest)
        del self._tmp_subpaths[oid]

    def _do_delete(self, oid):
        """Script command: delete an object.
        """
        ops = self.ops
        path = self.get_path(oid)
        if path == self.basepath:
            # Delete the contents of the base directory.
            for fn in ops.listdir(path):
                if not fn in ('_root', '_tmp'):
                    self._rmrf(ops.join(self.basepath, fn))
        else:
            # Delete an object.
            if not ops.isdir(path):
                # Delete the annotation files also.
                extra = self.afs.get_annotation_paths(path)
                for s in extra:
                    if ops.exists(s):
                        ops.remove(s)
            self._rmrf(path)
        if self._tmp_subpaths.has_key(oid):
            del self._tmp_subpaths[oid]
        parents = self.table.get_parents(oid)
        for parent_oid, filename in parents:
            self.table.remove(parent_oid, filename)
            # XXX Need to garbage collect descendants in the OID table.


    def _do_write_all(self, container_changes):
        """Script command: write all objects.

        Uses multiple passes.

        container_changes: {oid: {filename: child_oid}}
        """
        ops = self.ops
        while self._pending:
            written = 0
            for oid, anns in self._pending.items():
                p = self.get_subpath(oid)
                if p is None:
                    # Not linked into the object system yet.
                    # Try again on the next pass.
                    continue
                path = ops.join(self.basepath, *p)
                t = anns[node_type_ann]
                if not ops.exists(path):
                    if t == 'd':
                        ops.mkdir(path)
                to_write = {}
                for name, value in anns.items():
                    if (name == node_type_ann
                        or name == suggested_extension_ann):
                        # Doesn't need to be written.
                        continue
                    elif name == data_ann:
                        data, as_text = value
                        ops.writefile(path, as_text, data)
                    elif name == file_list_ann:
                        # Prepare the object_names annotation.
                        object_names = []
                        for objname, child_oid in value:
                            object_names.append(objname)
                        to_write[object_names_ann] = '\n'.join(object_names)
                        # Move objects from the temporary directory.
                        fn_oid = container_changes.get(oid)
                        if fn_oid:
                            for filename, child_oid in fn_oid.items():
                                self.table.add(oid, filename, child_oid)
                                if self._tmp_subpaths.has_key(child_oid):
                                    self._restore(child_oid)
                        self.afs.invalidate(path)
                    else:
                        to_write[name] = value
                self.afs.write_annotations(path, to_write)
                self.afs.invalidate(self.ops.dirname(path))
                # This object has been written.
                written += 1
                del self._pending[oid]

            if not written:
                # Nothing was written in this pass.  This means that
                # the rest of the queued objects are not actually
                # linked into the object system.  Toss them.
                if DEBUG:
                    tossing = self._pending.keys()
                    tossing.sort()
                    print "fs: tossing %s" % ', '.join(tossing)
                break


    def _do_link_app(self, app_exists):
        """Script command: link or unlink the application object at the root.
        """
        path = self.ops.join(self.basepath, '_root', self.app_filename)
        if app_exists:
            # The root has an application.  Represent it with a directory.
            if not self.ops.exists(path):
                self.ops.makedirs(path)
        else:
            # The root does not have an application.  Remove it.
            if self.ops.exists(path):
                self.ops.rmtree(path)

    #
    # ITPCConnection implementation
    #

    def sortKey(self):
        return self.basepath

    def getName(self):
        return self.basepath

    def connect(self):
        ops = self.ops
        if not ops.exists(self.basepath):
            ops.makedirs(self.basepath)
        if self.app_filename:
            # If there are objects at basepath, create a _root
            # containing an application also.
            contents = self.afs.compute_contents(self.basepath)
            fn_to_name, name_to_fn = contents
            if fn_to_name:
                self._do_link_app(1)

    def begin(self):
        self.afs.clear_cache()

    def vote(self):
        """Do some early verification

        This is done while the transaction can still be vetoed safely.
        """
        self._prepare()
        self._final = 1

    def abort(self):
        self.reset()

    def finishWrite(self):
        if self._final:
            for code in self._script:
                m = getattr(self, '_do_%s' % code[0])
                m(*code[1:])

    def finishCommit(self):
        if self._final:
            self.reset()

    def close(self):
        self.reset()
