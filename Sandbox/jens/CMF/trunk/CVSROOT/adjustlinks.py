#!/bin/env python

"""Adjust symlinks in the repository according to the repolinks recipe file.

The repolinks file is found in the CVSROOT of the repository, along with this
script.

The links asserted by repolinks are compared with existing links in the
filesystem, and links are added and deleted as necessary.  See
LinkManager.assert_map() for specifics.

Errors - illegal or invalid paths, collisions, etc - are reported to
stderr.

See RepoUtils.postcommit and .adjustlinks for more details (generally
installed in the python site-packages directory)."""

from RepoUtils.adjustlinks import cvs_adjustlinks

cvs_adjustlinks(recipe_name="repolinks", quiet=0)
