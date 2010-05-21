import re
import zc.buildout.testing

import unittest
import zope.testing
from zope.testing import doctest, renormalizing
import getpass
import os
import os.path
import stat
import logging
import pwd
import pprint
import grp

here = os.path.abspath(os.path.dirname(__file__))
user = pwd.getpwuid(os.geteuid()).pw_name
group = grp.getgrgid(os.getegid()).gr_name

def buildout_pprint(buildout):
    b_dict = dict((key, dict(value)) for (key, value) in buildout.iteritems())
    string = pprint.pformat(b_dict).replace('\\n', '\n')
    print string

def setupBuildout(test, *args):
    rmdir, write, tmpdir = (
        test.globs['rmdir'],
        test.globs['write'],
        test.globs['tmpdir'])
    args = list(args)
    cfg = args.pop()
    filename = args.pop()
    directory = os.path.join(*args)
    eggs = os.path.join(os.path.join(directory, 'eggs'))
    eggs = os.path.join(os.path.join(directory, 'eggs'))
    path = os.path.join(directory, filename)
    install_eggs = test.globs.get('eggs', tuple())
    sample_buildout = test.globs['sample_buildout']
    rmdir(directory)
    test.globs['sample_buildout'] = sample_buildout = tmpdir(sample_buildout)
    write(path, cfg)
    os.chdir(sample_buildout)
    buildout = zc.buildout.buildout.Buildout(
        path,
        [# trick bootstrap into putting the buildout develop egg
        # in the eggs dir.
        ('buildout', 'develop-eggs-directory', 'eggs'),
        ],
        user_defaults=False
        )
    # Create the develop-eggs dir, which didn't get created the usual
    # way due to the trick above:
    os.mkdir('develop-eggs')

    #Raise the log threshold for the bootstrap, because we don't care about
    #it
    logger = logging.getLogger('zc.buildout')
    level = logging.getLogger('zc.buildout').level
    logging.getLogger('zc.buildout').setLevel(99999)
    buildout.bootstrap([])
    logging.getLogger('zc.buildout').setLevel(level)

    #Remove extra log handlers that dump output outside of the test or mess
    #the test up.
    logger.removeHandler(logger.handlers[0])
    if logger.parent:
        logger.parent.removeHandler(logger.parent.handlers[1])

    #Install the eggs we need.
    for egg in install_eggs:
        zc.buildout.testing.install(egg, eggs)
    return buildout


def ls(path):
    def perm(power, mode):
        bit = (mode & 2 ** power) << (31 - power)
        if bit:
            if power in [2, 5, 8]:
                return 'r'
            elif power in [1, 4, 7]:
                return 'w'
            else:
                return 'x'
        else:
            return '-'
    st = os.stat(path)
    if stat.S_ISDIR(st.st_mode):
        permissions = ['d']
    else:
        permissions = ['-']
    permissions = ''.join(permissions + [perm(power, st.st_mode) for power in reversed(xrange(9))])
    return '%s %s %s %s' % (permissions, user, group, path)

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('zc.recipe.wrapper', test)
    test.globs['user'] = getpass.getuser()
    test.globs['ls'] = ls
    test.globs['here'] = here
    test.globs['wrapper'] = os.path.abspath(os.path.join(here,'../../../..'))
    test.globs['setupBuildout'] = (
        lambda *args: setupBuildout(test, ('zc.recipe.egg',), *args))
    test.globs['buildout_pprint'] = buildout_pprint
    os.chdir(test.globs['wrapper'])


def test_suite():
    return unittest.TestSuite((
        #doctest.DocTestSuite(),
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            checker=renormalizing.RENormalizing([
                (re.compile('\d+ \d\d\d\d-\d\d-\d\d \d\d:\d\d'), ''),
                (re.compile(user), 'USER'),
                (re.compile(group), 'GROUP'),
                (re.compile('/.*/sample-buildout'), 'PREFIX'),
               ]),
            optionflags = (zope.testing.doctest.REPORT_NDIFF
                           | zope.testing.doctest.ELLIPSIS)
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
