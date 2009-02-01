Persistent Python modules allow us to develop and store Python modules in the
ZODB in contrast to storing them on the filesystem. You might want to look at
the `zodbcode` package for the details of the implementation. In Zope 3 we
implemented persistent modules as utilities. These utilities are known as
module managers that manage the source code, compiled module and name of the
module. We then provide a special module registry that looks up the utilities
to find modules.
