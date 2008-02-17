z3c.autoinclude
===============

This package adds a new directive: "autoinclude". This directive
searches through the dependencies in your setup.py file
(install_requires), and includes the meta.zcml and configure.zcml
files in those packages that it finds. Inclusion order matches the
order in the setup.py file. You can pass a path for the package you
want to autoinclude for, but typically you pass in the current
package, as follows: <autoinclude package="." />

The motivation behind this is to prevent having to repeat yourself in
2 places, the setup.py file, and including the zcml. Common errors,
especially for beginners, is to add a new dependency, but to forget to
include the zcml as well. With the autoinclude directive, adding the
includes for the zcml is no longer necessary.

This can eventually be used with grok, and grokproject. Creating a new
grokproject can add this directive in the zcml, and then you no longer
have to worry about including the zcml manually.
