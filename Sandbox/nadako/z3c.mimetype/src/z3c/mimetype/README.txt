Mime type guessing
==================

This package provides an utility for guessing mime type from filename and/or 
file contents. It's based on freedesktop.org's shared-mime-info database.

The `shared-mime-info <http://freedesktop.org/wiki/Software/shared-mime-info>`_
is a extensible database of common mime types. It provides powerful mime type
detection mechanism as well as multi-lingual type descriptions.

This package requires shared-mime-info to be installed and accessible. The
easiest way to do that is to install it system-wide, for example installing
the ``shared-mime-info`` package on Ubuntu. The specification_ also describes
other ways to install and extend the database.

.. _specification: http://standards.freedesktop.org/shared-mime-info-spec/shared-mime-info-spec-0.13.html#s2_layout

The core of this package is the global IMIMETypesUtility component.

  >>> from zope.component import getUtility
  >>> from zope.interface.verify import verifyObject
  >>> from z3c.mimetype.interfaces import IMIMETypesUtility

  >>> util = getUtility(IMIMETypesUtility)
  >>> verifyObject(IMIMETypesUtility, util)
  True

It has three methods for getting mime type. Those three methods are
``getTypeByFileName``, ``getTypeByContents`` and ``getType``. We will
describe them in that order, but for applications, it's reccommended to
use the latter, ``getType`` method as it's most generic and easy-to use.

The simpliest method is ``getTypeByFileName`` that looks up the type by
filename.

  >>> mt = util.getTypeByFileName('example.doc')

The mime type is the object implementing IMIMEType interface.

  >>> from zope.interface.verify import verifyObject
  >>> from z3c.mimetype.interfaces import IMIMEType

  >>> verifyObject(IMIMEType, mt)
  True

  >>> mt.media
  'application'

  >>> mt.subtype
  'msword'

  >>> str(mt)
  'application/msword'

MIMEType object also has a title attribute that is a translatable string.

  >>> mt.title
  u'application/msword'  

  >>> from zope.i18nmessageid.message import Message
  >>> isinstance(mt.title, Message)
  True

Shared-Mime-Info is nice, it can even detect mime type for file names like
``Makefile``.

  >>> print util.getTypeByFileName('Makefile')
  text/x-makefile

Also, it know the difference in extension letter case. For example the ``.C``
should be detected as C++ file, when ``.c`` is plain C file.

  >>> print util.getTypeByFileName('hello.C')
  text/x-c++src
  
  >>> print util.getTypeByFileName('main.c')
  text/x-csrc

The method returns None if it can determine type from file name.

  >>> print util.getTypeByFileName('somefilename')
  None

Another useful method is ``getTypeByContents``. It's first argument should
be an opened file. Also, it can take min_priority and max_priority arguments,
but it's only useful if you know the shared-mime-info specification.

We have some sample files that should be detected by contents

  >>> import os
  >>> def openSample(extension):
  ...     return open(os.path.join(SAMPLE_DATA_DIR, 'sample.' + extension))

  >>> fdoc = openSample('doc')
  >>> print util.getTypeByContents(fdoc)
  application/msword

  >>> fhtml = openSample('html')
  >>> print util.getTypeByContents(fhtml)
  text/html
  
  >>> fpdf = openSample('pdf')
  >>> print util.getTypeByContents(fpdf)
  application/pdf

  >>> fpng = openSample('png')
  >>> print util.getTypeByContents(fpng)
  image/png

If we pass the file without any magic bytes, it will return None

  >>> funknown = openSample('unknown')
  >>> print util.getTypeByContents(funknown)
  None

And finally, the most useful method is simply ``getType``. It accepts
two arguments - the filename and opened file object. At least one of
them should be specified. This method tries to guess the mime type
as specified in shared-mime-info specification document and always returns
some useful mimetype (application/octet-stream or text/plain if cannot 
detect).

It needs at least one argument, so you can't call it with no arguments.

  >>> util.getType()
  Traceback (most recent call last):
  ...
  TypeError: Either filename or file should be provided or both of them

  >>> print util.getType(filename='wrong.doc')
  application/msword

  >>> print util.getType(file=fpng)
  image/png

If type cannot be detected, it WILL return either text/plain or
application/octet-stream mime type. It will try to guess is it text
or binary by checking first 32 bytes. 

  >>> print util.getType(filename='somefile', file=funknown)
  text/plain

  >>> funknownbinary = openSample('binary')
  >>> print util.getType(filename='somefile2', file=funknownbinary)
  application/octet-stream

Let's close files, because we won't need them anymore.

  >>> del fdoc, fhtml, fpdf, fpng, funknown, funknownbinary

Finally, let's check the i18n features that comes with shared-mime-info
and are supported by this package. All mimetype titles are translatable
messages and can be easily rendered in UI.

Let's get some mime type to play with.

  >>> mt = util.getTypeByFileName('example.png')

By default, mimetype title message id is its media/subtype form.

  >>> mt.title
  u'image/png'

But if we translate it, we'll get a human-friendly string.

  >>> from zope.i18n import translate
  
  >>> translate(mt.title)
  u'PNG image'

  >>> translate(mt.title, target_language='ru')
  u'\u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 PNG'
