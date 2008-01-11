##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Create the grok reference in various output formats."""

import sys
import re
import time
import os
import os.path

from docutils import nodes, SettingsSpec
from docutils.core import publish_cmdline, publish_file, default_description
from docutils.core import default_usage, default_description
from docutils.frontend import OptionParser
from docutils.readers.standalone import Reader
from docutils.transforms import Transform
from docutils.transforms.universal import FilterMessages
from docutils.parsers.rst import Parser
from docutils.writers.s5_html import Writer as S5Writer
from docutils.writers.html4css1 import Writer as HTMLWriter
from docutils.writers.latex2e import Writer as LaTeX2eWriter

# Register plain (non-sphinx) directives and roles.
from extensions import directives_plain, roles_plain


class AdditionalSubstitutions(Transform):
    """Substitute keywords based on the settings `substitutions`
    dictionary.
    """
    default_priority = 210
    
    def apply(self):
        config = self.document.settings
        substitutions = config.substitutions
        for ref in self.document.traverse(nodes.substitution_reference):
            refname = ref['refname']
            text = substitutions.get(refname, None)
            ref.replace_self(nodes.Text(text, text))
        return

class ReferenceReader(Reader):
    """A reader that performs additional substitutions.
    """
    def get_transforms(self):
        tf = Reader.get_transforms(self)
        return tf + [AdditionalSubstitutions, FilterMessages]


class ReferenceParser(Parser):
    """A marker class."""
    pass


class ReferenceHTMLWriter(HTMLWriter):
    """A marker class. Generates HTML."""
    pass

class ReferenceS5Writer(S5Writer):
    """A marker class. Generates HTML Slides."""
    pass


class ReferenceLaTeX2eWriter(LaTeX2eWriter):
    """A marker class. Generates LaTeX."""
    pass


class ReferencePublisher(object):
    """A publisher for reference docs in ReST format.

    Renders the ReST files of a directory into HTML.
    """

    settings = {}
    usage = '%prog [options] <source-dir> [<destination-dir>]'
    description = ('Generates reference documents from standalone '
                   'reStructuredText sources. '
                   ' '
                   'If no destination directory is given, everything '
                   'will be rendered into the source directory. '
                   )

    def __init__(self):
        self.reader = ReferenceReader()
        self.parser = ReferenceParser()
        self.writer = ReferenceHTMLWriter()
        
        # Substitutions, that should be replaced during rendering...
        self.subs = {
            'today': time.strftime('%B %d, %Y'),
            'version': 'unknown',
            'release': 'unknown'
        }

        # Default settings for reading, parsing, writing...
        self.settings = {
            'halt_level': 6,
            'input_encoding': 'utf8',
            'output_encoding': 'utf8',
            'initial_header_level': 2,
            # don't try to include the stylesheet (docutils gets hiccups)
            #'stylesheet_path': '',
            'substitutions': self.subs,
        }

        # Read settings with commandline options set...
        self.processCommandLine(usage=self.usage,
                                description=self.description,
                                **self.settings)

        self.subs['version'] = self.getVersionInfo()
        self.subs['release'] = self.subs['version']
        # The source directory...
        self.dirname = os.path.normpath(os.path.abspath(
            self.settings['_source']))
        self.filelist = self.getFileList(self.dirname, '*.rst')
        return


    def getFileList(self, dirname, pattern):
        """Get the list of files we will parse.
        """
        import fnmatch
        try:
            if os.path.isfile(dirname):
                return [dirname]
        except OSError:
            return []
        try:
            result = [filename for filename in os.listdir(dirname)
                      if fnmatch.fnmatch(filename, pattern) and
                      os.path.isfile(os.path.join(dirname, filename))]
        except OSError:
            return []
        result.sort()
        return result

    def setupOptionParser(self, usage=None, description=None,
                            settings_spec=None, config_section=None,
                            **defaults):
        """Setup options for commandline.
        """
        if config_section:
            if not settings_spec:
                settings_spec = SettingsSpec()
            settings_spec.config_section = config_section
            parts = config_section.split()
            if len(parts) > 1 and parts[-1] == 'application':
                settings_spec.config_section_dependencies = ['applications']
        option_parser = OptionParser(
            components=(self.parser, self.reader, self.writer, settings_spec),
            defaults=defaults, read_config_files=1,
            usage=usage, description=description)
        return option_parser


          
    def processCommandLine(self, argv=None, usage=None, description=None,
                             settings_spec=None, config_section=None,
                             **defaults):
        """
        Pass an empty list to `argv` to avoid reading `sys.argv` (the
        default).
        """
        option_parser = self.setupOptionParser(
            usage, description, settings_spec, config_section, **defaults)
        if argv is None:
            argv = sys.argv[1:]
        settings = option_parser.parse_args(argv)
        # Turn the `optparse` values instance in `settings` into a
        # real dictionary, so that is can be handled by docutils
        # publishers.
        self.settings = {}
        for key, val in settings.__dict__.items():
            self.settings[key] = val
        return


    def getVersionInfo(self):
        """Determine the release number.

        We read the version info from the setup.py file two
        directories above.
        """
        selfdir = os.path.dirname(__file__)
        setup_file = os.path.join(selfdir, '..', '..', 'setup.py')
        setup_file = os.path.abspath(setup_file)
        try:
            fp = open(setup_file, 'r')
        except OSError:
            return 'unknown'
        reg_exp = re.compile("^\s*version\s*=\s*('|\")(.+)('|\")\s*")
        for line in fp:
            m = reg_exp.match(line)
            if not m:
                continue
            return m.groups()[1]
        return 'unknown'


    def getInOutFilenames(self, filename):
        """Compute the absolute filenames of input and output based on
        commandline parameters.
        """
        src_path = os.path.abspath(os.path.join(self.dirname, filename))
        if self.settings['_destination'] is not None:
            dest_path = os.path.join(self.settings['_destination'], filename)
        else:
            dest_path = src_path
        dest_path = os.path.splitext(dest_path)[0] + '.html'
        return (src_path, dest_path)


    def publish(self):
        """Generate the reference.

        Read a bunch of files, render and output it. TOCtrees and
        references are not resolved in this plain version.
        """
        print "Reading sources from %s." % (self.dirname,)
        for filename in self.filelist:
            src_path, dest_path = self.getInOutFilenames(filename)
            print "Writing %s..." %  dest_path
            publish_file(
                source_path=src_path,
                destination_path=dest_path,
                reader=self.reader,
                writer=self.writer,
                parser=self.parser,
                settings_overrides=self.settings
                )
        return

def main():
    reference = ReferencePublisher().publish()

if __name__ == '__main__':
    main()
