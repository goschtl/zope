This package provides a few simple scripts to administrate the Python Package
Index (PyPI).

Adding and Removing Roles
-------------------------

The first two scripts allow to grant or revoke the owner role to/from a user
for a list of packages. Here is the syntax::

  # addrole --user=USER --pwd=PASSWORD TARGETUSER PACKAGE1, PACKAGE2, ...
  # delrole --user=USER --pwd=PASSWORD TARGETUSER PACKAGE1, PACKAGE2, ...

Optionally, you can also apply the role changes to all packages of the calling
user::

  # addrole --user=USER --pwd=PASSWORD -a TARGETUSER
  # delrole --user=USER --pwd=PASSWORD -a TARGETUSER
