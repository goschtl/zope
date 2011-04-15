# Copyright (c) 2010 Zope Foundation and Contributors
# See also LICENSE.txt

import sys
import mimetypes
import os
import os.path
import subprocess
import re

COPYRIGHT_PATTERN = re.compile(
    '^(?P<lead>.*)Copyright \\(c\\) '
    '(?P<periods>[0-9\-, ]+) (?P<owner>.*?)(?P<tail>\W*)$')

LICENSE_PATTERN = re.compile(
    '^(?P<lead>.*)Version (?P<version>.*) \(ZPL\)\.')

ALIEN_ZVSL_LICENSE_PATTERN = re.compile(
    '^(?P<lead>.*)Version (?P<version>.*) \(ZVSL\)\.')


def walk_project_dir(root, callback):
    def visit(args, dirname, names):
        for name in list(names):
            if name.startswith('.'):
                names.remove(name)
                continue
            if name.endswith('.egg-info'):
                names.remove(name)
                continue
            if os.path.splitext(name)[1] in [
                    '.so', '.pyc', '.pyo']:
                continue
            if os.path.isfile(os.path.join(dirname, name)):
                path = os.path.join(dirname, name)
                m_type, enc = mimetypes.guess_type(path)
                if m_type is not None:
                    callback(path)
    os.path.walk(root, visit, ())


class Checker(object):

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    license_name = 'ZPL'
    license_version = '2.1'
    copyright_holder = 'Zope Foundation and Contributors'

    def __init__(self, working_dir):
        self.working_dir = os.path.abspath(working_dir)
        self.log = []

    def run(self):
        if not os.path.isdir(self.working_dir):
            self.log.append('Invalid folder path %s' % self.working_dir)
            return

        self.check_license_file()
        self.check_egg_metadata()
        self.check_copyright()

    def check_license_file(self):
        """Verifies license expression:

            - the file LICENSE.txt exists and has a valid copy of the ZPL 2.1
            - the file setup.py (if it exists) and is marked as ZPL 2.1

        """
        license = os.path.join(self.working_dir, 'LICENSE.txt')
        if not os.path.isfile(license):
            self.log.append('LICENSE.txt: Missing license file')
        else:
            license_content = open(license).read()
            license_expected = open(
                os.path.join(self.data_dir, 'ZPL-2.1.txt')).read()
            if license_content != license_expected:
                self.log.append('LICENSE.txt: Not a valid copy of ZPL 2.1')

    def check_egg_metadata(self):
        setup = os.path.join(self.working_dir, 'setup.py')
        if not os.path.isfile(setup):
            return
        environment = os.environ
        environment['PYTHONPATH'] = ':'.join(sys.path)
        s = subprocess.Popen([sys.executable, setup, 'egg_info'],
                             cwd=self.working_dir,
                             stdout=subprocess.PIPE,
                             env=environment)
        s.wait()
        s = subprocess.Popen([sys.executable, setup,
                              '--license'],
                             cwd=self.working_dir,
                             stdout=subprocess.PIPE,
                             env=environment)
        s.wait()
        metadata = s.stdout.readlines()
        if len(metadata) < 1 or len(metadata) % 1:
            self.log.append('setup.py: could not extract metadata')
            return
        while metadata:
            license, metadata = metadata[0], metadata[1:]
            license = license.strip()
            if not license.startswith(self.license_name):
                self.log.append(
                    'setup.py: license not declared as "%s" (found: "%s")' %
                    (self.license_name, license))

    def check_copyright(self):
        """Verifies the copyright assignment to the Zope Foundation

            - the file COPYRIGHT.txt exists and has correct content
            - all copyright statements that can be found refer to the Zope
              foundation
            - all license comments refer to the most recent version of ZPL

        """
        copyright = os.path.join(self.working_dir, 'COPYRIGHT.txt')
        if not os.path.isfile(copyright):
            self.log.append('COPYRIGHT.txt: Missing copyright file')
        else:
            content = open(copyright).read().strip()
            if content != self.copyright_holder:
                self.log.append(
                    'COPYRIGHT.txt: not assigned to "%s" '
                    '(found: "%s")' % (self.copyright_holder, content))
        walk_project_dir(self.working_dir, self._check_copyright_file)

    def _check_copyright_file(self, filename):
        for i, line in enumerate(open(filename)):
            m = COPYRIGHT_PATTERN.match(line)
            if m is not None:
                if m.group('owner') != self.copyright_holder:
                    self.log.append('%s:%i: incorrect copyright holder: %s' % (
                        filename.replace(self.working_dir + '/', ''), i + 1,
                        m.group('owner')))
                continue
            m = LICENSE_PATTERN.match(line)
            if m is not None:
                if m.group('version') != self.license_version:
                    self.log.append('%s:%i: incorrect ZPL version: %s' % (
                    filename.replace(self.working_dir + '/', ''), i + 1,
                    m.group('version')))
            m = ALIEN_ZVSL_LICENSE_PATTERN.match(line)
            if m is not None:
                self.log.append('%s:%i: incorrect license: ZVSL version: %s' % (
                        filename.replace(self.working_dir + '/', ''), i + 1,
                        m.group('version')))

def main():
    result = 0
    checker = Checker(sys.argv[1])
    checker.run()
    for entry in checker.log:
        result = 1
        print entry
    sys.exit(result)
