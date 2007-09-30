#!/usr/bin/python

import os

def setUp(test):
    import os.path, tempfile, StringIO, logging
    import pysvn

    # Create a repository in a temporary directory
    test.tmpdir = tempfile.mkdtemp()
    repo = os.path.join(test.tmpdir, 'repo')
    stdin, stdouterr = os.popen4('svnadmin create ' + repo)
    assert stdouterr.read() == ''
    assert stdin.close() is None
    assert stdouterr.close() is None

    # Import out test repository layout into the temporary repository
    url = 'file://' + repo
    testdir = os.path.dirname(__file__)
    pysvn.Client().import_(os.path.join(testdir, 'repo'), url, '_')

    # Construct an externals file from the template
    template = file(os.path.join(testdir, 'EXTERNALS.txt'))
    fd, externals_path = tempfile.mkstemp()
    externals = file(externals_path, 'w')
    externals.write(template.read() % {'tmpdir': test.tmpdir})
    externals.close()
    template.close()

    # Collect log
    log = StringIO.StringIO()
    logger = logging.getLogger('repoexternals')
    logger.addHandler(logging.StreamHandler(log))

    # Add names from setup to the test globals
    script = os.path.join(
        os.path.dirname(os.path.dirname(os.getcwd())),
        'bin', 'repoexternals')
    test.globs.update(script=script, url=url, log=log,
                      externals=externals_path)

    import z3c.repoexternals
    test.globs.update(z3c.repoexternals.__dict__)

def tearDown(test):
    import shutil
    shutil.rmtree(test.tmpdir)
    os.remove(test.globs['externals'])

def test_suite():
    import doctest
    return doctest.DocFileSuite(
        'functional.txt',
        'script.txt',
        setUp=setUp, tearDown=tearDown,
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='test_suite')
