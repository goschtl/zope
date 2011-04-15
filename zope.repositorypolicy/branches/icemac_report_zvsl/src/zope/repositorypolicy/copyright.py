# Copyright (c) 2010 Zope Foundation and Contributors
# See also LICENSE.txt

import StringIO
import os.path
import sys
import zope.repositorypolicy.project


class FixCopyrightHeaders(object):
    """A simple helper to fix source file copyright headers."""

    owner = zope.repositorypolicy.project.Checker.copyright_holder
    license_version = zope.repositorypolicy.project.Checker.license_version

    def __init__(self, working_dir):
        self.working_dir = os.path.abspath(working_dir)

    def run(self):
        zope.repositorypolicy.project.walk_project_dir(
            self.working_dir, self._fix_file)

        license = open(os.path.join(self.working_dir, 'LICENSE.txt'), 'w')
        license.write(open(os.path.join(
            os.path.dirname(__file__), 'data', 'ZPL-2.1.txt')).read())
        license.close()

        copyright = open(os.path.join(self.working_dir, 'COPYRIGHT.txt'), 'w')
        copyright.write(self.owner)
        copyright.close()

    def _fix_file(self, path):
        needs_fixing = False
        output = StringIO.StringIO()
        for line in open(path):
            m = zope.repositorypolicy.project.COPYRIGHT_PATTERN.match(line)
            if m is not None:
                new_line = '%sCopyright (c) %s %s%s' % (
                    m.group('lead'), m.group('periods'), self.owner,
                    m.group('tail'))
                if new_line != line:
                    line = new_line
                    needs_fixing = True
            m = zope.repositorypolicy.project.LICENSE_PATTERN.match(line)
            if m is not None:
                if m.group('version') != self.license_version:
                    new_line = line.replace(m.group('version'),
                                            self.license_version)
                    line = new_line
                    needs_fixing = True
            output.write(line)

        if needs_fixing:
            print 'Fixing: %s' % path
            open(path, 'w').write(output.getvalue())


def main():
    FixCopyrightHeaders(sys.argv[1]).run()
