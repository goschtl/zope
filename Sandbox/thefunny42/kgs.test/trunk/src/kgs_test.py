import logging
import os.path
import os
import popen2
import glob
from pkg_resources import Environment, WorkingSet
from zc.buildout import easy_install

# Configuration
ZOPE3_SVN = os.getenv('ZOPE3_SVN',
                      'svn://svn.zope.org/repos/main/')
DEVELOP_EGG = 'develop-eggs'
BLACKLIST = ['zope.agxassociation', 'zope.app.css', 'zope.app.demo', \
                 'zope.app.fssync', 'zope.app.recorder', \
                 'zope.app.schemacontent', 'zope.app.sqlexpr', \
                 'zope.app.styleguide', 'zope.app.tests', \
                 'zope.app.versioncontrol', 'zope.app.zopetop', \
                 'zope.bobo', 'zope.browserzcml2', 'zope.fssync', \
                 'zope.generic', 'zope.importtool', 'zope.kgs', \
                 'zope.release', 'zope.pytz', 'zope.timestamp', \
                 'zope.tutorial', 'zope.ucol', 'zope.weakset', \
                 'zope.webdev', 'zope.xmlpickle',]
DELETE_LIST = ['zope.app.boston',]
IGNORED = BLACKLIST + DELETE_LIST


def to_test(project, packages, check=False):
    """Gives back the egg to test.
    """
    if check:
        print "%s %s" % (project, packages[0].version)
        requires = packages[0].requires()
        for req in requires:
            if len(req.specs):
                print "Requirement %s" % req
    if 'test' in packages[0].extras:
        return project + ' [test]'
    return project

def main(egg_cache, download_cache):
    """Create buildout.cfg for running test independently on a set of
    packages.
    """

#     logger = logging.getLogger()
#     logger.setLevel(logging.DEBUG)
#     logging.basicConfig()

    # Collect project
    projects = []
    svn_list, _ = popen2.popen2("svn ls %s" % ZOPE3_SVN)
    for project in svn_list:
        project = project[:-2]
        if project in IGNORED:
            continue
        parts = project.split('.')
        if parts[0] in ('zope', 'grokcore', ):
            projects.append(project)

    # Write buildout and makefile
    kgs_conf = open('kgs.cfg', 'w')
    trunk_conf = open('trunk.cfg', 'w')
    makefile = open('Makefile', 'w')

    kgs_conf.write("""
[versions]
ZODB3 = 3.8

[buildout]
prefer-final = false
newest = true
unzip = true
versions = versions
parts = 
""")
    makefile.write("""
all: """)
    trunk_conf.write("""
[buildout]
extends = kgs.cfg
develop = 
""")

    for project in projects:
        script_name = project.replace('.', '-')
        kgs_conf.write("  test-%s\n" % script_name)
        makefile.write(" test-%s" % script_name)
        trunk_conf.write("  %s\n" % project)

    makefile.write("""

test-%:
	$(CURDIR)/bin/$@
""")

    if not os.path.isdir(DEVELOP_EGG):
        os.mkdir(DEVELOP_EGG)

    trunk_env = Environment([DEVELOP_EGG,])
    kgs_env = Environment([egg_cache,])
    kgs_ws = WorkingSet(kgs_env)
    easy_install.prefer_final(False)
    easy_install.download_cache(download_cache)

    for project in projects:
        if not os.path.isdir(project):
            os.system('svn co %s/%s/trunk %s' % (ZOPE3_SVN, project, project))

        script_name = project.replace('.', '-')

        # Released version
        easy_install.install([project],
                             os.path.abspath(egg_cache),
                             working_set=kgs_ws, newest=True)
        kgs_env = Environment([egg_cache,])
        kgs_ws = WorkingSet(kgs_env)
        packages = kgs_env[project]

        kgs_conf.write("""
[test-%s]
recipe = zc.recipe.testrunner
eggs = %s
""" % (script_name, to_test(project, packages, True)))

        # Trunk version
        packages = trunk_env[project]
        if not len(packages):
            easy_install.develop(os.path.abspath(project),
                                 os.path.abspath(DEVELOP_EGG))
            # Rescan evrything, trunk_env.scan don't seems to work
            trunk_env = Environment([DEVELOP_EGG,])
            packages = trunk_env[project]

        trunk_conf.write("""
[test-%s]
recipe = zc.recipe.testrunner
eggs = %s
""" % (script_name, to_test(project, packages)))


    # Clean develop-eggs, otherwise if you choose KGS you still have trunk
    for path in os.listdir(DEVELOP_EGG):
        os.remove(DEVELOP_EGG + '/' + path)

    # Create a default buildout.cfg if it doesn't exits yet.
    if not os.path.isfile('buildout.cfg'):
        buildout_conf = open('buildout.cfg', 'w')
        buildout_conf.write("""
[buildout]
extends = kgs.cfg
""")


if __name__ == '__main__':
    main()
