
import unittest

from zope.kgs.change import parseReleases

class ChangesTests(unittest.TestCase):

    kgs_changes = """
=======
CHANGES
=======

0.2.0 (2007-11-??)
------------------

- Initial version as ``zope.kgs``.

  * A script that lists all versions of a package released after the latest
    version lsited in the KGS.

  * A script that manages the generation of the entire KGS site.

  * Generate an intro page to the KGS.

  * Generate `links.html` file which lists all controlled packages files.

  * Features copied from ``zope.release``:

    + Parser for KGS configuration files.

    + Generate `versions.cfg` and `buildout.cfg` script.

  * Features copied from ``zc.mirrorcheeseshopslashsimple``:

    + Generate new index pages for the controlled packages.
"""

    def test_kgs_example(self):
        releases = list(parseReleases(self.kgs_changes))
        self.assertEqual(len(releases), 1)
        version, release_date, changes = releases[0]
        self.assertEqual(version, "0.2.0")
        self.assertEqual(release_date, "2007-11-??")
        self.assertEqual(len(changes), 22)

    datagenerator_changes = """
=======
CHANGES
=======

0.0.3 (2008-12-03)
------------------

- Refined the seed generation further: zlib.crc32() in 32 bit Python can
  generate negative hashes, while 64 bit Python does not.  Enforced
  positive hashes.

- Began a test suite.


0.0.2 (2008-12-02)
------------------

- Use the crc32 function to hash random seeds so that the
  same random sequences are generated on both 32 bit and 64 bit
  builds of Python.


0.0.1 (2008-02-14)
------------------

- Initial Release
"""

    def test_datagenerator_example(self):
        releases = list(parseReleases(self.datagenerator_changes))
        self.assertEqual(len(releases), 3)
        version, release_date, changes = releases[1]
        self.assertEqual(version, "0.0.2")
        self.assertEqual(release_date, "2008-12-02")
        self.assertEqual(len(changes), 6)

    zope_proxy_changes = """
=======
CHANGES
=======

3.5.0 (unreleased)
------------------

- Added support to bootstrap on Jython.

3.4.2 (2008/07/27)
------------------

- Made C code compatible with Python 2.5 on 64bit architectures.

1.0
---
- fake changelog entry here
"""
    def test_zope_proxy_example(self):
        releases = list(parseReleases(self.zope_proxy_changes))
        self.assertEqual(len(releases), 3)
        version, release_date, changes = releases[0]
        self.assertEqual(version, "3.5.0")
        self.assertEqual(release_date, "unreleased")
        self.assertEqual(len(changes), 3)

        version, release_date, changes = releases[2]
        self.assertEqual(version, "1.0")
        self.assertEqual(release_date, None)
        self.assertEqual(changes, ["- fake changelog entry here", ""])


if __name__ == '__main__':
    unittest.main()
