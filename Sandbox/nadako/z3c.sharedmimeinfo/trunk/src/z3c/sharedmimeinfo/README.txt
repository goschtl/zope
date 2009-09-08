==================
z3c.sharedmimeinfo
==================

This package provides an utility for guessing MIME type from file name and/or 
actual contents. It's based on freedesktop.org's shared-mime-info database.

.. contents::

Shared MIME info database
-------------------------

The `shared-mime-info <http://freedesktop.org/wiki/Software/shared-mime-info>`_
is a extensible database of common MIME types. It provides powerful MIME type
detection mechanism as well as multi-lingual type descriptions.

This package requires shared-mime-info to be installed and accessible. The
easiest way to do that is to install it system-wide, for example installing
the ``shared-mime-info`` package on Ubuntu. The specification_ also describes
other ways to install and extend the database.

.. _specification: http://standards.freedesktop.org/shared-mime-info-spec/shared-mime-info-spec-0.13.html#s2_layout

Thread-safety
-------------

Note, that this package is currently not thread-safe, because data are meant to
be loaded only once, on module import. If there will be any problems because of
that, it could be changed in future.

MIME type guessing
------------------

The easiest way to use this package is to import the ``getType`` function from
the root module::

  >>> from z3c.sharedmimeinfo import getType

This function tries to guess the MIME type as specified in shared-mime-info
specification document and always returns some usable MIME type, using
application/octet-stream or text/plain as fallback. It can detect MIME type by
file name, its contents or both, so it accepts two arguments: filename (string)
and/or file (file-like object). At least one of them should be given.

As said above, it needs at least one argument, so you can't call it with no
arguments::

  >>> getType()
  Traceback (most recent call last):
  ...
  TypeError: Either filename or file should be provided or both of them

Passing file name is done via the ``filename`` argument::

  >>> print getType(filename='document.doc')
  application/msword

Passing file contents is done via ``file`` argument, which accepts a file-like
object. Let's use our testing helper function to open a sample file and try
to guess a type for it::

  >>> print getType(file=openSample('png'))
  image/png

If the MIME type cannot be detected, either ``text/plain`` or
``application/octet-stream`` will be returned. The function will try to guess
is it text or binary by checking the first 32 bytes:: 

  >>> print getType(filename='somefile', file=openSample('text'))
  text/plain

  >>> print getType(filename='somefile', file=openSample('binary'))
  application/octet-stream

MIME type objects
-----------------

Objects returned by ``getType`` and other functions (see below) are actually
an extended unicode string objects, providing additional info about the MIME
type. They provide the IMIMEType interface::

  >>> from zope.interface.verify import verifyObject
  >>> from z3c.sharedmimeinfo.interfaces import IMIMEType

  >>> mt = getType(filename='document.doc')
  >>> verifyObject(IMIMEType, mt)
  True

As they are actually unicode objects, they can be compared like strings::

  >>> mt == 'application/msword'
  True

They also provides the ``media`` and ``subtype`` attributes::

  >>> mt.media
  u'application'

  >>> mt.subtype
  u'msword'

And finally, they provide the ``title`` attribute that is a translatable
message::

  >>> mt.title
  u'application/msword'  

  >>> from zope.i18nmessageid.message import Message
  >>> isinstance(mt.title, Message)
  True

Let's check the i18n features that comes with shared-mime-info and are
supported by this package. As seen above, the MIME type title message ID is
actually its <media>/<subtype>, but if we translate it, we'll get a
human-friendly string::

  >>> from zope.i18n import translate
  
  >>> translate(mt.title)
  u'Word document'

  >>> translate(mt.title, target_language='ru')
  u'\u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442 Word'

  >>> from z3c.sharedmimeinfo.mimetype import MIMEType

We can also create IMIMEType objects by hand, using the MIMEType class::

  >>> from z3c.sharedmimeinfo.mimetype import MIMEType

We can create them specifying media and subtype as two arguments or as a single
argument in the "media/subtype" form::

  >>> MIMEType('text/plain')
  <MIMEType text/plain>

  >>> MIMEType('image', 'png')
  <MIMEType image/png>

Note, that the MIMEType objects are cached, so if you you'll create another
object for the same mime type, you'll get the same object::

  >>> mt = MIMEType('text/plain')
  >>> mt2 = MIMEType('text/plain')
  >>> mt2 is mt
  True

Advanced usage
--------------

The ``getType`` function, described above is actually a method of the
IMIMETypesUtility object. The IMIMETypesUtility is a core component for
guessing MIME types.

Let's import the utility directly and play with it::

  >>> from z3c.sharedmimeinfo.utility import mimeTypesUtility

  >>> from z3c.sharedmimeinfo.interfaces import IMIMETypesUtility
  >>> verifyObject(IMIMETypesUtility, mimeTypesUtility)
  True

It has three methods for getting mime type. Those three methods are
``getType`` (described above), ``getTypeByFileName``, ``getTypeByContents``.

Detection by file name
~~~~~~~~~~~~~~~~~~~~~~

The ``getTypeByFileName`` method of the MIME types utility looks up the type
by filename::

  >>> mt = mimeTypesUtility.getTypeByFileName('example.doc')

shared-mime-info database is really nice, it can even detect mime type for
file names like ``Makefile``::

  >>> print mimeTypesUtility.getTypeByFileName('Makefile')
  text/x-makefile

Also, it know the difference in extension letter case. For example the ``.C``
should be detected as C++ file, when ``.c`` is plain C file::

  >>> print mimeTypesUtility.getTypeByFileName('hello.C')
  text/x-c++src
  
  >>> print mimeTypesUtility.getTypeByFileName('main.c')
  text/x-csrc

The method will return ``None`` if it fails determining type from file name::

  >>> print mimeTypesUtility.getTypeByFileName('somefilename')
  None

Detection by contents
~~~~~~~~~~~~~~~~~~~~~

The ``getTypeByContents`` method accepts a file-like object and two optional
arguments: min_priority and max_priority that can be used to specify the range
of "magic" rules to be used. By default, min_priority is 0 and max_priority is
100, so all rules will be in use. See shared-mime-info specification for
details.

We have some sample files that should be detected by contents::

  >>> fdoc = openSample('doc')
  >>> print mimeTypesUtility.getTypeByContents(fdoc)
  application/msword

  >>> fhtml = openSample('html')
  >>> print mimeTypesUtility.getTypeByContents(fhtml)
  text/html
  
  >>> fpdf = openSample('pdf')
  >>> print mimeTypesUtility.getTypeByContents(fpdf)
  application/pdf

  >>> fpng = openSample('png')
  >>> print mimeTypesUtility.getTypeByContents(fpng)
  image/png

If we pass the file without any known magic bytes, it will return ``None``::

  >>> funknown = openSample('binary')
  >>> print mimeTypesUtility.getTypeByContents(funknown)
  None

  >>> del fdoc, fhtml, fpdf, fpng, funknown
