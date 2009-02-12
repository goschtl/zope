import sys
import os.path
import optparse
import shutil
import tempfile
import pkg_resources
import paste.script.command

def create_project(paste_template):
    usage = "usage: %prog [options] PROJECT"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--no-buildout', action="store_true", dest="no_buildout",
                      default=False, help="Only create project area, do not "
                      "bootstrap the buildout.")
    parser.add_option('--svn-repository', dest="repos", default=None,
                      help="Import project to given repository location (this "
                      "will also create the standard trunk/ tags/ branches/ "
                      "hierarchy).")
    parser.add_option('--newer', action="store_true", dest="newest",
                      default=False, help="Check for newer versions of packages.")
    parser.add_option('-v', '--verbose', action="store_true", dest="verbose",
                      default=False, help="Be verbose.")
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_usage()
        return 1

    exit_code = run_paster_create(paste_template,
                                  project=args[0],
                                  repos=options.repos,
                                  verbose=options.verbose,
                                  newest=options.newest)

    if not options.no_buildout:
        # TODO exit_code
        os.chdir(args[0])
        run_buildout(options.verbose)

def run_paster_create(paste_template, project, repos=None, verbose=False,
                      newest=False):
    """Run paster create.

    This will create a sandbox using a paste.script template.
    """
    option_args = []
    if repos is not None:
        option_args.extend(['--svn-repository', repos])
    if not verbose:
        option_args.append('-q')

    extra_args = []
    if newest:
        extra_args.append('newest=true')
    else:
        extra_args.append('newest=false')

    commands = paste.script.command.get_commands()
    cmd = commands['create'].load()
    runner = cmd('create')
    return runner.run(option_args + ['-t', paste_template, project]
                      + extra_args)

def run_buildout(verbose=False):
    """Run a buildout.

    This will download zc.buildout if it's not available. Then it will
    bootstrap the buildout scripts and finally launch the buildout
    installation routine.

    Note that this function expects the buildout directory to be the
    current working directory.
    """
    extra_args = []
    if not verbose:
        extra_args.append('-q')

    try:
        import zc.buildout.buildout
    except ImportError:
        print "Downloading zc.buildout..."

        # Install buildout into a temporary location
        import setuptools.command.easy_install
        tmpdir = tempfile.mkdtemp()
        sys.path.append(tmpdir)
        setuptools.command.easy_install.main(extra_args +
                                             ['-mNxd', tmpdir, 'zc.buildout'])

        # Add downloaded buildout to PYTHONPATH by requiring it
        # through setuptools (this dance is necessary because the
        # temporary installation was done as multi-version).
        ws = pkg_resources.working_set
        ws.add_entry(tmpdir)
        ws.require('zc.buildout')

        import zc.buildout.buildout
        zc.buildout.buildout.main(extra_args + ['bootstrap'])
        shutil.rmtree(tmpdir)
    else:
        zc.buildout.buildout.main(extra_args + ['bootstrap'])

    print "Invoking zc.buildout..."
    zc.buildout.buildout.main(['-q', 'install'])
