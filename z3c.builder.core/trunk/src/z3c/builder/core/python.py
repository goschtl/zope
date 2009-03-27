##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Python Builder Components

$Id$
"""
import types
import zope.interface
from zope.schema.fieldproperty import FieldProperty
from z3c.builder.core import base, interfaces


class ModuleBuilderGetter(object):
    zope.interface.implements(interfaces.IModuleBuilderGetter)

    def getModuleBuilder(self):
        module = self
        while not interfaces.IModuleBuilder.providedBy(module):
            module = module.__parent__
            if module is None:
                raise ValueError(
                    'No module builder was found and the root node of '
                    'the project tree was reached.')
        return module


class PackageBuilder(base.DirectoryBuilder):
    zope.interface.implements(interfaces.IPackageBuilder)

    initTemplate = base.getTemplatePath('__init__.py')
    initNamespaceTemplate = base.getTemplatePath('__init__namespace.py')
    packageName = FieldProperty(interfaces.IPackageBuilder['packageName'])

    def __init__(self, name, packageName=None):
        if packageName is None:
            packageName = str(name)
        super(PackageBuilder, self).__init__(name, packageName)
        self.packageName = packageName

    def getPythonPath(self):
        if interfaces.IPythonPathRoot.providedBy(self.__parent__):
            return self.packageName
        if self.__parent__ is None:
            return self.packageName
        return self.__parent__.getPythonPath() + '.' + str(self.packageName)

    def update(self):
        """See interfaces.IBaseBuilder"""
        super(PackageBuilder, self).update()
        matches = [subBuilder for subBuilder in self.values()
                   if (interfaces.IFileBuilder.providedBy(subBuilder) and
                       subBuilder.filename == '__init__.py')]
        if matches:
            return
        template = self.initTemplate
        try:
            project = self.getProject()
        except ValueError:
            project = None
        if project and self.getPythonPath() in project.setup.namespace_packages:
            template = self.initNamespaceTemplate
        self['__init__.py'] = base.SimpleFileBuilder(
            u'__init__.py', template)


class ModuleBuilder(base.BuilderContainer, base.FileBuilder):
    zope.interface.implements(interfaces.IModuleBuilder)

    moduleName = FieldProperty(interfaces.IModuleBuilder['moduleName'])
    imports = FieldProperty(interfaces.IModuleBuilder['imports'])

    def __init__(self, name, moduleName=None):
        super(ModuleBuilder, self).__init__(name)
        if moduleName is None:
            moduleName = str(name)[:-3]
        self.moduleName = moduleName
        self.filename = str(name)

    def getPythonPath(self):
        return self.__parent__.getPythonPath() + '.' + str(self.moduleName)

    def update(self):
        self.imports = []
        super(ModuleBuilder, self).update()

    def render(self):
        """See interfaces.IContentBuilder"""
        output = []
        # Render comment header.
        project = self.getProject()
        output.append(project.commentHeader)
        # Render module doc string.
        output.append('"""Module Documentation"""\n')
        # Render imports making sure none is duplicated.
        for path in sorted(set(self.imports)):
            module, name = tuple(path.rsplit('.', 1))
            if module != self.getPythonPath():
                output.append('from %s import %s\n' % (module, name))
        output.append('\n\n')
        # Render all sub-builders.
        for subBuilder in self.values():
            output.append(subBuilder.render())
            output.append('\n\n')
        # Return a concatenated version of all pieces.
        return ''.join(output)


class FieldBuilder(ModuleBuilderGetter, base.ContentBuilder):
    zope.interface.implements(interfaces.IFieldBuilder)

    fieldName = FieldProperty(interfaces.IFieldBuilder['fieldName'])
    type = FieldProperty(interfaces.IFieldBuilder['type'])
    attributes = FieldProperty(interfaces.IFieldBuilder['attributes'])
    indent = FieldProperty(interfaces.IFieldBuilder['indent'])

    _numberOfSpaces = 4

    def __init__(self, name, type, indent=0, **attributes):
        self.name = name
        self.type = type
        self.indent = indent
        self.attributes = attributes

    def update(self):
        self.getModuleBuilder().imports.append(self.type)

    def render(self):
        indent = ' ' * (self.indent * self._numberOfSpaces)
        output = ''
        output += indent + '%s = %s(' %(self.name, self.type.rsplit('.')[-1])
        if self.attributes:
            output += '\n'
        indent += ' ' * (self._numberOfSpaces)
        for item in reversed(self.attributes.items()):
            output += indent + '%s=%r,\n' %item
        if self.attributes:
            output += indent
        output += ')\n'
        return output


class FunctionBuilder(ModuleBuilderGetter, base.ContentBuilder):
    zope.interface.implements(interfaces.IFunctionBuilder)

    fieldName = FieldProperty(interfaces.IFieldBuilder['fieldName'])
    type = FieldProperty(interfaces.IFieldBuilder['type'])
    attributes = FieldProperty(interfaces.IFieldBuilder['attributes'])
    indent = FieldProperty(interfaces.IFieldBuilder['indent'])

    _numberOfSpaces = 4

    def __init__(self, name, args=(), kwargs=None,
                 docstring='', indent=0, code=''):
        self.name = name
        self.args = args
        self.kwargs = (kwargs and dict(kwargs)) or {}
        self.docstring = docstring
        self.indent = indent
        self.code = code

    def render(self):
        # Generate the proper indentation level.
        indent = ' ' * (self.indent * self._numberOfSpaces)
        output = ''
        # Render the first part of the function header.
        output += indent+'def %s(' %str(self.name)
        # Render the position arguments.
        output += ', '.join([str(arg) for arg in self.args])
        if self.args and self.kwargs:
            output += ', '
        # Render keyword arguments.
        output += ', '.join(['%s=%r' %item for item in self.kwargs.items()])
        output += '):\n'
        # Render body of function
        indent += self._numberOfSpaces * ' '
        if self.docstring:
            output += indent + '"""%s"""' %self.docstring
        if self.code:
            output += '\n'
            for line in self.code.split('\n'):
                output += indent + line + '\n'
        if not self.code and not self.docstring:
            output += indent + 'pass'
        output += '\n'
        return output


class InterfaceBuilder(ModuleBuilderGetter,
                       base.BuilderContainer, base.ContentBuilder):
    zope.interface.implements(interfaces.IInterfaceBuilder)

    docstring = FieldProperty(interfaces.IInterfaceBuilder['docstring'])
    bases = FieldProperty(interfaces.IInterfaceBuilder['bases'])

    def __init__(self, name):
        super(InterfaceBuilder, self).__init__(name)
        self.docstring = ''
        self.bases = []

    def add(self, builder):
        if isinstance(builder, (FunctionBuilder, FieldBuilder)):
            builder.indent = 1
        return super(InterfaceBuilder, self).add(builder)

    def getPythonPath(self):
        return self.__parent__.getPythonPath() + '.' + str(self.name)

    def update(self):
        if len(self.bases) == 0:
            self.bases = ['zope.interface.Interface']
        self.getModuleBuilder().imports += self.bases
        for builder in self.values():
            builder.update()

    def render(self):
        bases = [path.rsplit('.', 1)[-1] for path in self.bases]
        output = ''
        output += 'class %s(%s):\n' %(str(self.name), ', '.join(bases))
        output += '    """%s"""\n' %self.docstring
        for builder in self.values():
            output += builder.render()
            output += '\n'
        return output


class ClassFromInterfaceBuilder(ModuleBuilderGetter, base.ContentBuilder):
    zope.interface.implements(interfaces.IClassFromInterfaceBuilder)

    interface = FieldProperty(
        interfaces.IClassFromInterfaceBuilder['interface'])
    bases = FieldProperty(
        interfaces.IClassFromInterfaceBuilder['bases'])
    docstring = FieldProperty(
        interfaces.IClassFromInterfaceBuilder['docstring'])
    implementations = FieldProperty(
        interfaces.IClassFromInterfaceBuilder['implementations'])

    def __init__(self, name, interface, bases=None):
        super(ClassFromInterfaceBuilder, self).__init__(name)
        self.interface = interface
        self.bases = list(bases) if bases is not None else []
        self.docstring = ''
        self.implementations = {}

    def _resolve(self, path):
        pieces = path.split('.')
        # Find package root.
        root = self
        while not interfaces.IPythonPathRoot.providedBy(root.__parent__):
            root = root.__parent__
        # Find builder
        path = ''
        builder = root
        for piece in pieces:
            if path:
                path += '.'
            path += piece
            for sub in builder.values():
                if (hasattr(sub, 'getPythonPath') and
                    path == sub.getPythonPath()):
                    builder = sub
                    break
        return builder

    def addImplementation(self, name, code):
        self.implementations[name] = code

    def getPythonPath(self):
        return self.__parent__.getPythonPath() + '.' + str(self.name)

    def update(self):
        # Determine the bases
        if len(self.bases) == 0:
            self.bases = ['object']
        self.getModuleBuilder().imports += self.bases
        # Compute the interface, if necessary
        if isinstance(self.interface, types.StringTypes):
            self.interface = self._resolve(self.interface)
        # Add import for interface
        self.__parent__.imports.append('zope.interface.implements')
        self.__parent__.imports.append(self.interface.getPythonPath())
        # Generate docstring if necessary
        if not self.docstring:
            self.docstring = "Implementation of ``%s``" % self.interface.getPythonPath()
        # Generate fields and methods
        self.fields = [entry for entry in self.interface.values()
                       if isinstance(entry, FieldBuilder)]
        self.methods = [entry for entry in self.interface.values()
                       if isinstance(entry, FunctionBuilder)]
        # Add imports if needed
        if len(self.fields):
            self.__parent__.imports.append(
                'zope.schema.fieldproperty.FieldProperty')

    def render(self):
        bases = [path.rsplit('.', 1)[-1] for path in self.bases]
        output = ''
        output += 'class %s(%s):\n' %(self.name, ', '.join(bases))
        output += '    """%s"""\n' %self.docstring
        output += '    implements(%s)\n\n' %self.interface.name
        for field in self.fields:
            output += "    %s = FieldProperty(%s['%s'])\n" %(
                field.name, self.interface.name, field.name)
        output += '\n'
        for method in self.methods:
            output += '    def %s(' %method.name
            allargs = ['self']
            allargs += [str(arg) for arg in method.args]
            allargs += ['%s=%r' %item for item in method.kwargs.items()]
            output += ', '.join(allargs)
            output += '):\n'
            output += '        """See ``%s``."""\n' %self.interface.getPythonPath()
            if method.name in self.implementations:
                impl = self.implementations[method.name]
                output += ' '*8
                output += impl.replace('\n', '\n'+' '*8)
            output += '\n'
        return output
