====================================
Schema directory for ZConfig schemas
====================================

In order to use the schema.xml file as a base for other schemas it has
to be accessible via a relative url. This will not work if we have an
egg based package. So for any package that is released as an egg we
add an svn:external to this location to reference the file.

