##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id$
"""
__metaclass__ = type

from interfaces import ISchemaSpec
from persistent import Persistent
from zope.app.schemagen.modulegen import generateModuleSource
from zope.interface import implements

_helper_import = 'from zope.app.schemagen import schemaspec'
_helper_module = 'schemaspec'

class SchemaSpec(Persistent):
    implements(ISchemaSpec)

    def __init__(self, schema_name, class_name=None):
        if class_name is None:
            class_name = schema_name + 'Class'
            if class_name.startswith('I'):
                class_name = class_name[1:]
        self._schema_name = schema_name
        self._class_name = class_name
        self._fields = {}
        self._field_names = []
        self._current_version = 0
        self._history = []

    def _appendHistory(self, action):
        self._history.append(action)
        self._current_version += 1

    def addField(self, name, field):
        if name in self._fields:
            raise KeyError, "Field %s already exists." % name
        # XXX should check name is a sensible pythonic name
        self._field_names.append(name)
        self._fields[name] = field
        action = AddField(name)
        self._appendHistory(action)
        self._p_changed = 1
        return action

    def removeField(self, name):
        if name not in self._fields:
            raise KeyError, "Field %s does not exist." % name
        del self._fields[name]
        self._field_names.remove(name)
        action = RemoveField(name)
        self._appendHistory(action)
        self._p_changed = 1
        return action

    def renameField(self, orig_name, target_name):
        if orig_name not in self._fields:
            raise KeyError, "Field %s does not exist." % orig_name
        if target_name in self._fields:
            raise KeyError, "Field %s already exists." % target_name
        # XXX should check target_name is pythonic
        position = self._field_names.index(orig_name)
        self._field_names[position] = target_name
        self._fields[target_name] = self._fields[orig_name]
        del self._fields[orig_name]
        action = RenameField(orig_name, target_name)
        self._appendHistory(action)
        self._p_changed = 1
        return action

    def insertField(self, name, field, position):
        if name in self._fields:
            raise KeyError, "Field %s already exists." % name
        if not 0 <= position <= len(self._field_names):
            raise IndexError, "Position %s out of range." % name
        # XXX should check name is pythonic
        self._fields[name] = field
        self._field_names.insert(position, name)
        action = InsertField(name, position)
        self._appendHistory(action)
        self._p_changed = 1
        return action

    def moveField(self, name, position):
        if name not in self._fields:
            raise KeyError, "Field %s does not exist." % name
        if not 0 <= position <= len(self._field_names):
            raise IndexError, "Position %s out of range." % name
        self._field_names.remove(name)
        self._field_names.insert(position, name)
        action = MoveField(name, position)
        self._appendHistory(action)
        self._p_changed = 1
        return action

    def getFieldsInOrder(self):
        """Get all fields in order as (name, field) tuples.
        """
        return [(field_name, self._fields[field_name])
                for field_name in self._field_names]

    def getCurrentVersion(self):
        return self._current_version

    def getHistory(self):
        return self._history

    def generateSetstateSource(self):
        lines = [
        'transformations = %s.prepareSetstate(self, state, %r)' % (
            _helper_module, self._current_version),
        'if transformations is None:',
        '    return',
        'dict = self.__dict__'
        ]
        count = self._current_version - len(self._history)
        for item in self._history:
            args = ', '.join(map(repr, item.code()))
            if args:
                args = ', '+args
            lines.append('if %s in transformations:' % count)
            lines.append('    %s.%s.update(dict, state%s)' % (
                _helper_module, type(item).__name__, args))
            count += 1

        method_text_list = ['    def __setstate__(self, state):']
        # indent by 8:       '12345678%s'
        method_text_list += ['        %s' % line for line in lines]
        return '\n'.join(method_text_list) + '\n'

    def generateModuleSource(self):
        if not self._history:
            # don't generate any __setstate__ when there is no history
            # to update from
            return generateModuleSource(
                self._schema_name, self.getFieldsInOrder(),
                self._class_name, schema_version=self._current_version)
        else:
            return generateModuleSource(
                self._schema_name, self.getFieldsInOrder(),
                self._class_name,
                schema_version=self._current_version,
                extra_imports=_helper_import,
                extra_methods=self.generateSetstateSource())

# future plans, perhaps:
# make each of these classes have views, and a method that
# returns a clear explanation of the consequences of this change
# for instances of the schema class.
# Make the history viewable by schema authors.
# Make individual items in the history turn-off-and-on-able
# so that you can choose to treat an add.... remove-add as a no-op,
# and preserve the state of instances.
class AddField:
    def __init__(self, name):
        self.name = name

    def code(self):
        return (self.name,)

    def update(dict, state, name):
        # clear the way for any default value if schema changes are
        # undone
        try:
            del dict[name]
        except KeyError:
            pass
    update = staticmethod(update)

class RemoveField:
    def __init__(self, name):
        self.name = name

    def code(self):
        return (self.name,)

    def update(dict, state, name):
        del dict[name]
    update = staticmethod(update)

class RenameField:
    def __init__(self, original, target):
        self.original = original
        self.target = target

    def code(self):
        return self.original, self.target

    def update(dict, state, original, target):
        del dict[original]
        dict[target] = state[original]
    update = staticmethod(update)

class InsertField:
    def __init__(self, name, position):
        self.name = name
        self.position = position

    def code(self):
        return self.name, self.position

    def update(dict, state, name, position):
        pass
    update = staticmethod(update)

class MoveField:
    def __init__(self, name, position):
        self.name = name
        self.position = position

    def code(self):
        return self.name, self.position

    def update(dict, state, name, position):
        pass
    update = staticmethod(update)

def prepareSetstate(obj, state, schema_version):
    obj.__dict__.update(state)
    state_version = state['__schema_version__']
    if schema_version == state_version:
        return None
    assert state_version < schema_version
    obj.__schema_version__ = schema_version
    d = {}
    for i in range(state_version, schema_version):
        d[i] = 1
    return d
