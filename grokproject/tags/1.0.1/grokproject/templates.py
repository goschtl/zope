import sys
import os
import urllib2
import urlparse
import xml.sax.saxutils
from paste.script import templates
from paste.script.templates import NoDefault
from grokproject.utils import run_buildout
from grokproject.utils import ask_var
from grokproject.utils import get_boolean_value_for_option
from grokproject.utils import get_sha1_encoded_string
from grokproject.utils import create_buildout_default_file
from grokproject.utils import exist_buildout_default_file
from grokproject.utils import required_grok_version
from grokproject.utils import extend_versions_cfg

GROK_RELEASE_URL_DEFAULT = 'http://grok.zope.org/releaseinfo/'


class GrokProject(templates.Template):
    _template_dir = 'template_paste'
    summary = "A grok project"
    required_templates = []

    vars = [
        ask_var('user', 'Name of an initial administrator user',
                default=NoDefault),
        ask_var('passwd', 'Password for the initial administrator user',
                default=NoDefault, should_echo=False),
        ask_var('newest', 'Check for newer versions of packages',
                default='false', should_ask=False,
                getter=get_boolean_value_for_option),
        ask_var('run_buildout',
                "After creating the project area, run the buildout.",
                default=True, should_ask=False,
                getter=get_boolean_value_for_option),
        ask_var('eggs_dir',
                'Location where zc.buildout will look for and place packages',
                default='', should_ask=False),
        ask_var('grok_release_url',
                "URL where grokproject will look up grok version and "
                "release information.",
                should_ask=False),
        ]

    def check_vars(self, vars, cmd):
        if vars['package'] in ('grok', 'zope'):
            print
            print "Error: The chosen project name results in an invalid " \
                  "package name: %s." % vars['package']
            print "Please choose a different project name."
            sys.exit(1)

        explicit_eggs_dir = vars.get('eggs_dir')
        grok_release_url = vars.get('grok_release_url',
                                    GROK_RELEASE_URL_DEFAULT)
        if not grok_release_url.endswith('/'):
            grok_release_url += '/'

        skipped_vars = {}
        for var in list(self.vars):
            if not var.should_ask:
                skipped_vars[var.name] = var.getter(vars, var)
                self.vars.remove(var)

        vars = super(GrokProject, self).check_vars(vars, cmd)
        for name in skipped_vars:
            vars[name] = skipped_vars[name]

        vars['grok_release_url'] = grok_release_url

        vars['passwd'] = get_sha1_encoded_string(vars['passwd'])            
        for var_name in ['user', 'passwd']:
            # Escape values that go in site.zcml.
            vars[var_name] = xml.sax.saxutils.quoteattr(vars[var_name])
        vars['app_class_name'] = vars['project'].capitalize()

        create_zopectl = False
        if vars.get('zopectl','') == 'True':
            create_zopectl = True
        if create_zopectl:
            self._template_dir = 'template_zopectl'

        # Handling the version.cfg file.
        print "Downloading info about versions..."
        version = vars.get('grokversion', 'current')
        cfg_filename = 'grok-%s.cfg' % version
        if version == 'current':
            # if no version was specified, we look up the current
            # version first
            current_info_url = urlparse.urljoin(grok_release_url, 'current')
            cfg_filename = self.download(current_info_url).strip()

        version_info_url = urlparse.urljoin(grok_release_url, cfg_filename)
        vars['version_info_url'] = version_info_url
        vars['version_info_file_contents'] = self.download(version_info_url)

        # Maybe add additional eggs...
        vars['version_info_additions'] = extend_versions_cfg(
            vars['version_info_file_contents'], create_zopectl)

        # Which grok version are we depending on?
        version = required_grok_version(vars['version_info_file_contents'])
        vars['grokversion'] = version

        buildout_default = exist_buildout_default_file()
        if explicit_eggs_dir:
            # Put explicit_eggs_dir in the vars; used by the post command.
            vars['explicit_eggs_dir'] = explicit_eggs_dir
            vars['eggs_dir'] = (
                '# Warning: when you share this buildout.cfg with friends\n'
                '# please remove the eggs-directory line as it is hardcoded.\n'
                'eggs-directory = %s') % explicit_eggs_dir
        elif buildout_default:
            vars['eggs-dir'] = ''
        else:
            create_buildout_default_file()

        vars['package_directory'] = os.path.abspath(os.path.join(
                os.getcwd(), vars['project']))
        
        return vars
    
    def download(self, url):
        """Downloads a file and returns the contents.

        If an error occurs, we abort, giving some information about
        the reason.
        """
        contents = None
        try:
            contents = urllib2.urlopen(url).read()
        except urllib2.HTTPError:
            # Some 404 or similar happened...
            print "Error: cannot download required %s" % url
            print "Maybe you specified a non-existing version?"
            sys.exit(1)
        except IOError, e:
            # Some serious problem: no connect to server...
            print "Error: cannot download required %s" % version_info_url
            print "Server may be down.  Please try again later."
            sys.exit(1)
        return contents
    
    def post(self, command, output_dir, vars):
        if not vars['run_buildout']:
            return
        original_dir = os.getcwd()
        os.chdir(vars['project'])
        run_buildout(command.options.verbose)
        os.chdir(original_dir)
