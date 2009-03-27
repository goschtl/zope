==========================
The Zope 3 Project Builder
==========================

The Zope 3 Project Builder was designed to interpret a high-level feature list
into a functional Python project. This package implements the code generation
pieces without worrying about the high-level features.

This package uses the concept of builders to construct a new project. The
process of building consists of two phases: (1) updating, and (2)
rendering/writing. Only (1) is well-defined at the fundamental level. In
addition, every builder *must* have a name.

  >>> from z3c.builder.core import base
  >>> builder = base.BaseBuilder(u'myBuilder')
  >>> builder
  <BaseBuilder u'myBuilder'>

  >>> builder.name
  u'myBuilder'
  >>> builder.update()
  Updating <BaseBuilder u'myBuilder'>

Builders often use sub-builders to complete the rendering. So another
important base class is the builder container:

  >>> container = base.BuilderContainer(u'myContainer')
  >>> container.add(builder)
  u'myBuilder'

  >>> container.update()
  Updating <BuilderContainer u'myContainer'>
  Updating <BaseBuilder u'myBuilder'>

  >>> container.remove(builder)
  >>> container.keys()
  []

It is also an ordered container:

  >>> container.add(base.BaseBuilder(u'n1'))
  u'n1'
  >>> container.add(base.BaseBuilder(u'n2'))
  u'n2'

  >>> container.keys()
  [u'n1', u'n2']
  >>> container.updateOrder([u'n2', u'n1'])
  >>> container.keys()
  [u'n2', u'n1']


Rendering versus Writing
------------------------

Beyond the base builder, there are two types of builders, the ones that render
content and the ones the write files/directories.

The basic content rendering builder is named `ContentBuilder`.

  >>> content = base.ContentBuilder(u'content')
  >>> content
  <ContentBuilder u'content'>

Every content builder must implement the `render()` method:

  >>> content.render()
  Traceback (most recent call last):
  ...
  NotImplementedError: The `render()` method is not implemented by
                       <ContentBuilder u'content'>.

As you can see the `ContentBuilder` class is meant to be used as a base class.

Let's now look at builders that write files. They are known as filesystem
builders.

  >>> fs = base.FilesystemBuilder(u'fs')
  >>> fs
  <FilesystemBuilder u'fs'>

Every filesystem builder must implement the `write(target)` method, where the
target is a path to the directory the builder is writing to.

  >>> fs.write(buildPath)
  Traceback (most recent call last):
  ...
  NotImplementedError: The `write(target)` method is not implemented.

There are two implementations of the filesystem builder, the
`DirectoryBuilder` and the `FileBuilder` class.

The name of the directory builder is used as the initial directory name that
it creates.

  >>> dir = base.DirectoryBuilder(u'myDir')
  >>> dir
  <DirectoryBuilder u'myDir'>
  >>> dir.dirname
  'myDir'

When the builder is written, it creates the directory.

  >>> dir.update()
  Updating <DirectoryBuilder u'myDir'>
  >>> dir.write(buildPath)
  Creating directory .../myDir

The name of the file builder is used to create the filename as well.

  >>> file = base.FileBuilder(u'myFile.txt')
  >>> file
  <FileBuilder u'myFile.txt'>
  >>> file.filename
  'myFile.txt'

When the builder is written, it creates the file. It turns out that the file
builder is both, a filesystem and content builder.

  >>> file.update()
  Updating <FileBuilder u'myFile.txt'>

  >>> file.write(buildPath)
  Traceback (most recent call last):
  ...
  NotImplementedError: The `render()` method is not implemented.

So, the `render()` method is not implemented. However, there is a simple file
builder that creates files based on a template file.

  >>> import os
  >>> template = os.path.join(buildPath, 'template.txt')
  >>> open(template, 'w').write('File Contents')

  >>> file = base.SimpleFileBuilder(u'rendered.txt', template)
  >>> file.update()
  Updating <SimpleFileBuilder u'rendered.txt'>
  >>> file.write(buildPath)
  Creating file .../rendered.txt

Let's now look at the generated file.

  >>> more(buildPath, 'rendered.txt')
  File Contents

Those are all the basic builders. In the "Specific Builders" section below you
can find a list of documents that document the fully implemented
builders. Those builders can be used to build full projects.


Builder Classes Layout
----------------------

A layout (UML class diagram) of all builder classes can be found at::

  ./class-diagram.png

All green classes can be used directly for building a project. Yellow and red
classes are meant to be used as abstract builder classes.


Specific Builders
-----------------

- ``project.txt``

  Documents the project builder, the most upper-level builder.

- ``python.txt``

  Documents and demonstrates builders that produce Python code.

- ``setup.txt``

  Documents the setup builder which generates the `setup.py` file.

- ``buildout.txt``

  Documents the buidlout builder that generates the ``buildout.cfg`` file.

- ``zcml.txt``

  Documents the generation of ZCML directives.

- ``form.txt``

  Documents the builders for `z3c.form`-based forms.
