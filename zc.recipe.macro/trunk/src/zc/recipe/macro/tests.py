##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import difflib
import logging
import os
import os.path
import pprint
import re
import zc.buildout.buildout
import zc.buildout.testing
import zc.buildout.tests
import zc.buildout.easy_install
import StringIO
import sys
import traceback

import unittest
import zc.recipe.egg
import zc.recipe.macro
import zc.recipe.testrunner
import zope.testing
import zope.testing.doctest
import zope.testing.renormalizing
import manuel
import manuel.doctest
import manuel.testing
import textwrap
import ConfigParser


here = os.path.abspath(os.path.dirname(__file__))

def buildout_pprint(buildout):
    b_dict = dict((key, dict(value)) for (key, value) in buildout.iteritems())
    string = pprint.pformat(b_dict).replace('\\n', '\n')
    print string

def setupBuildout(test, install_eggs=tuple(), *args):
    tmpdir, rmdir, write, sample_buildout = (
        test.globs['tmpdir'],
        test.globs['rmdir'],
        test.globs['write'],
        test.globs['sample_buildout'],)

    args = list(args)
    cfg = args.pop()
    filename = args.pop()
    directory = os.path.join(*args)
    eggs = os.path.join(os.path.join(directory, 'eggs'))
    path = os.path.join(directory, filename)
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
    logger = logging.getLogger('zc.buildout')
    logging.getLogger('zc.buildout').setLevel(99999)
    logger.removeHandler(logger.handlers[0])
    buildout.bootstrap([])
    for egg in install_eggs:
        zc.buildout.testing.install(egg, eggs)
    return buildout


class BuildoutEvaluation(object):
    def __init__(self, example, source=None, actual=None, desired=None, traceback=None):
        self.example = example
        self.traceback = traceback
        self.actual = actual
        self.desired = desired
        if traceback:
            self.passed = False
        else:
            # If there's no traceback, then we need to evaluate the results
            # 1) The result begins as a copy of the full generated buildout
            # 2) Sections and values that are not explicitly desired, and
            #    and are present in the source are removed, since they
            #    aren't interesting
            # 3) The result should be equivalent to the desired dictionary
            #    to pass

            self.result = dict(actual)
            for section_key, section in actual.iteritems():
                if section_key in source:
                    if section_key not in desired:
                        del self.result[section_key]
                    else:
                        for key, value in dict(section).iteritems():
                            if key in source[section_key]:
                                if key not in desired[section_key]:
                                    del self.result[section_key][key]
            self.passed = self.result == self.desired

    def test_sections(self, actual, desired):
        return list(key for key in desired
            if key in actual and actual[key] == desired[key])


def cfg_to_dict(cfg):
    config = ConfigParser.RawConfigParser()
    config.readfp(StringIO.StringIO(cfg))
    return dict(
        (section, dict(pair for pair in config.items(section)))
        for section in config.sections())

def dict_to_cfg(d):
    cp = ConfigParser.RawConfigParser()
    for section_name, section in d.iteritems():
        cp.add_section(section_name)
        for key, val in section.iteritems():
            cp.set(section_name, key, val)
    sio = StringIO.StringIO()
    cp.write(sio)
    cfg = sio.getvalue()
    sio.close()
    return cfg


START_RE = re.compile(r'^Buildout::$', re.MULTILINE)
END_RE = re.compile(r'(.+?)\n(?=\n\S).+?Result::(.+?)\n(?=\n\S)',
    re.DOTALL)

class BuildoutManuel(object):
    def parse(self, document):
        document.regions = document.find_regions(START_RE, END_RE)
        for region in document:
            buildout, want = [textwrap.dedent(s.lstrip('\n'))
                for s in region.end_match.groups()]
            example = zope.testing.doctest.Example(
                buildout, want, lineno=region.lineno + 2)
            document.replace_region(region, example)
            region.parsed = example

    def evaluate(self, document):
        setupBuildout = self.test.globs['setupBuildout']
        sample_buildout = self.test.globs['sample_buildout']
        rmdir = self.test.globs['rmdir']
        for region in document:
            example = region.parsed
            if not isinstance(example, zope.testing.doctest.Example):
                continue
            buildout = setupBuildout(
                sample_buildout, "buildout.cfg", example.source)
            try:
                buildout.install([])
                result_buildout = dict(buildout)
                region.evaluated = BuildoutEvaluation(example,
                                                      source=cfg_to_dict(example.source),
                                                      actual=result_buildout,
                                                      desired=cfg_to_dict(example.want))
            except zc.buildout.easy_install.MissingDistribution, md:
                region.evaluated = BuildoutEvaluation(
                    example, traceback=''.join(
                        traceback.format_exception(*(sys.exc_info()))))

    def format(self, document):
        for region in document:
            evaluation = region.evaluated
            if not isinstance(evaluation, BuildoutEvaluation):
                continue
            if not evaluation.passed:
                if evaluation.traceback:
                    region.formatted = evaluation.traceback
                else:
                    region.formatted = '\n'.join(list(difflib.unified_diff(
                        dict_to_cfg(evaluation.desired).split('\n'),
                        dict_to_cfg(evaluation.result).split('\n'),
                        'desired', 'result')))

    def setUp(self, test):
        self.test = test
        setUp(test)


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)

    test.globs['here'] = here
    test.globs['macro'] = os.path.join('../../../..', here)
    test.globs['setupBuildout'] = (
        lambda *args: setupBuildout(test, (), *args))
    test.globs['buildout_pprint'] = buildout_pprint
    os.chdir(test.globs['macro'])
    return test

def tearDown(test):
    zc.buildout.testing.rmdir(test.globs['sample_buildout'])
    zc.buildout.testing.buildoutTearDown(test)

def test_suite():
    optionflags = (zope.testing.doctest.NORMALIZE_WHITESPACE
                   | zope.testing.doctest.ELLIPSIS
                   | zope.testing.doctest.REPORT_NDIFF)
    suite = unittest.TestSuite()
    suite.addTest(
        zope.testing.doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=tearDown,
            checker=zope.testing.renormalizing.RENormalizing([
               zc.buildout.testing.normalize_path,
               zc.buildout.testing.normalize_script,
               zc.buildout.testing.normalize_egg_py,
               zc.buildout.tests.normalize_bang,
               ]), optionflags=optionflags
            ),)

    m = manuel.doctest.Manuel(
        optionflags=(zope.testing.doctest.NORMALIZE_WHITESPACE |
                     zope.testing.doctest.ELLIPSIS))

    bm = BuildoutManuel()
    manuel_test = manuel.Manuel()
    manuel_test.parser(timing='early')(bm.parse)
    manuel_test.evaluater(bm.evaluate)
    manuel_test.formatter(bm.format)

    m.extend(manuel_test)
    quickstart = manuel.testing.TestSuite(m, 'QUICKSTART.txt', setUp=bm.setUp)
    suite.addTest(quickstart)

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


