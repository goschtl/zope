==============
Using zc.index
==============

The `zc.index` package provides various adapters that provide for
searchable text extraction.  Many of these adapters require running
external applications over data stored in file objects (as defined in
the `zope.file` package); these adapters should only be registered if
the required applications are available on the host platform.  The
presence of the external application should not also require that the
adapter be registered.

To support this manner of configuration, ZCML conditions are used to
determine which adapters should be enabled.  The conditions should be
set only if the required application is available and should be used.
Such features should be defined in the top-level *site.zcml* file or
some other file included from that after `zope.mimetype` configuration
has been loaded and the before the `zc.index` configuration is loaded.

The following conditional features are used by `zc.index`:

program:pdftotext
  This indicates that the **pdftotext** tool from **xpdf** has been
  installed and should be used by the application server.  When set,
  `zc.index` will be able to extract text from PDF files.

program:wvWare
  The indicates that the **wvWare** tool is available and can be used
  by the application server.  When set, `zc.index` will be able to
  extract text from Microsoft Word files.
