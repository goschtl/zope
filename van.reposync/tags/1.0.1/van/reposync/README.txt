Mirror a pypi-style egg repository from a debian APT repository

Disclaimer
----------

This package depends on an as-yet-unreleased version of python-apt (0.8) for
which it seems the only download location is debian's experimental
distribution. Currently the version there is 0.7.91.

While this code is tested for simple cases, a lot of the different failure
modes have not been tested. So if it breaks for you, please add your failure to
the automated tests and submit a patch!

Use
---

Doctest setup (so we can test the documentation):
    
    >>> import tempfile, os
    >>> tmp_dir = tempfile.mkdtemp()

    >>> from van.reposync import tests
    >>> tests_dir = os.path.dirname(tests.__file__)
    >>> sources1_list = os.path.join(tmp_dir, 'sources1.list')
    >>> open(sources1_list, 'w').write(open(os.path.join(tests_dir, 'sources1.list'), 'r').read() % {'tests_dir': tests_dir})

We provide one binary `van-reposync` which can be run to perform the
synchronization. The first time it's run, it requires an --apt-sources
parameter pointing at an apt sources.list file containing the apt-repositories
you wish to mirror. It is important that the .list file contain matching deb
and deb-src lines (mirroring needs both binary and source packages): 

    >>> tests.runit('van-reposync sync --root %s --apt-sources %s' % (tmp_dir, sources1_list))

After it's done, you will see that the directory you pointed the tool at
contains an apt configuration, buildout configuration and tarballs linked into
a pypi-style repository.

The next run does not require the apt-sources command, and should be a lot faster:

    >>> tests.runit('van-reposync sync --root %s' % tmp_dir)

TearDown

    >>> import shutil
    >>> shutil.rmtree(tmp_dir)
