import os.path
import os
import popen2
import glob
from pkg_resources import Environment, WorkingSet
from zc.buildout import easy_install


ZOPE3_SVN = os.getenv('ZOPE3_SVN', 'svn://svn.zope.org/repos/main/')
EGG_CACHE = os.getenv('EGG_CACHE', '/Users/sylvain/Library/Buildout/eggs')
DEVELOP_EGG = 'develop-eggs'
NEWEST = False
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

wanted = []
svn_list, _ = popen2.popen2("svn ls %s" % ZOPE3_SVN)
for project in svn_list:
    project = project[:-2]
    if project in IGNORED:
        continue
    parts = project.split('.')
    if parts[0] in ('zope', 'grokcore', ):
        wanted.append(project)


kgs_conf = open('kgs.cfg', 'w')
trunk_conf = open('trunk.cfg', 'w')
makefile = open('Makefile', 'w')

kgs_conf.write("""
[buildout]
extends = versions.cfg
#versions = versions
newest = true
unzip = true
parts = 
""")
makefile.write("""
all: """)
trunk_conf.write("""
[buildout]
extends = kgs.cfg
develop = 
""")


for project in wanted:
    script_name = project.replace('.', '-')
    kgs_conf.write("  test-%s\n" % script_name)
    makefile.write(" test-%s" % script_name)
    trunk_conf.write("  %s\n" % project)

makefile.write("""

test-%:
	$(CURDIR)/bin/$@
""")

def to_test(project, need_test):
    if need_test:
        return project + ' [test]'
    return project

kgs_env = Environment([EGG_CACHE,])
kgs_ws = WorkingSet(kgs_env)
trunk_env = Environment([DEVELOP_EGG,])

for project in wanted:
    print project
    if not os.path.isdir(project):
        os.system('svn co %s/%s/trunk %s' % (ZOPE3_SVN, project, project))

    packages = kgs_env[project]
    kgs_need_test = False
    if not len(packages):
        easy_install.install(project, EGG_CACHE, newest=NEWEST, working_set=kgs_ws)
        packages = kgs_env[project]
    kgs_need_test = 'test' in packages[0].extras

    packages = trunk_env[project]
    trunk_need_test = False
    if not len(packages):
        easy_install.develop(os.path.abspath(project), os.path.abspath(DEVELOP_EGG))
        # Rescan evrything, trunk_env.scan don't seems to work
        trunk_env = Environment([DEVELOP_EGG,])
        packages = trunk_env[project]

    trunk_need_test = 'test' in packages[0].extras

    script_name = project.replace('.', '-')

    kgs_conf.write("""
[test-%s]
recipe = zc.recipe.testrunner
eggs = %s
""" % (script_name, to_test(project, kgs_need_test)))
    trunk_conf.write("""
[test-%s]
recipe = zc.recipe.testrunner
eggs = %s
""" % (script_name, to_test(project, trunk_need_test)))


# Clean develop-eggs, otherwise if you choose KGS you still have trunk
for path in os.listdir(DEVELOP_EGG):
    os.remove(DEVELOP_EGG + '/' + path)
