# Copyright (c) 2010 Zope Foundation and Contributors
# See also LICENSE.txt

import sys
import zope.repositorypolicy.project
import StringIO


class FixCopyrightHeaders(object):
    """A simple helper to fix source file copyright headers."""

    def __init__(self, working_dir, owner):
        self.working_dir = working_dir
        self.owner = owner

    def run(self):
        zope.repositorypolicy.project.walk_project_dir(
            self.working_dir, self._fix_file)

    def _fix_file(self, path):
        print path
        output = StringIO.StringIO()
        for line in open(path):
            m = zope.repositorypolicy.project.COPYRIGHT_PATTERN.match(line)
            if m is not None:
                line = '%sCopyright (c) %s %s%s' % (
                    m.group('lead'), m.group('periods'), self.owner,
                    m.group('tail'))
            output.write(line)
        open(path, 'w').write(output.getvalue())


def main():
    FixCopyrightHeaders(sys.argv[1], sys.argv[2]).run()
