# Copyright (c) 2010 Zope Foundation and Contributors
# See also LICENSE.txt

import sys
import os
import os.path
import subprocess
import re

COPYRIGHT_PATTERN = re.compile(
    '^(?P<lead>.*)Copyright \\(c\\) '
    '(?P<periods>[0-9\-, ]+) (?P<owner>.*?)(?P<tail>\W*)$')


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
                callback(path)
    os.path.walk(root, visit, ())


class Checker(object):

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    license_name = 'ZPL 2.1'
    copyright_holder = 'Zope Foundation and Contributors'

    def __init__(self, working_dir):
        self.working_dir = os.path.abspath(working_dir)
        self.log = []

    def run(self):
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
        s = subprocess.Popen([sys.executable, setup,
                              '--license', '--author'],
                             cwd=self.working_dir,
                             stdout=subprocess.PIPE,
                             env=environment)
        s.wait()
        metadata = s.stdout.readlines()
        if len(metadata) != 2:
            self.log.append('setup.py: could not extract metadata')
            return
        license = metadata[0].strip()
        if license != self.license_name:
            self.log.append(
                'setup.py: license not declared as "%s" (found: "%s")' %
                (self.license_name, license))
        author = metadata[1].strip()
        if author != self.copyright_holder:
            self.log.append(
                'setup.py: author not declared as "%s" '
                '(found: "%s")' %
                (self.copyright_holder, author))

    def check_copyright(self):
        """Verifies the copyright assignment to the Zope Foundation

            - the file COPYRIGHT.txt exists and has correct content
            - all copyright statements that can be found refer to the Zope
              foundation

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
            if m is None:
                continue
            if m.group('owner') != self.copyright_holder:
                self.log.append('%s:%i: incorrect copyright holder: %s' % (
                    filename.replace(self.working_dir + '/', ''), i + 1,
                    m.group('owner')))


def main():
    result = 0
    checker = Checker(sys.argv[1])
    checker.run()
    for entry in checker.log:
        result = 1
        print entry
    sys.exit(result)
