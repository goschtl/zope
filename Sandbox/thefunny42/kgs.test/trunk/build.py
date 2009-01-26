
import os.path
import popen2

ZOPE3_SVN = "svn://svn.zope.org/repos/main/"

wanted = []
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

for project in wanted:
    kgs_conf.write("""
[test-%s]
recipe = zc.recipe.testrunner
eggs = %s
""" % (project.replace('.', '-'), project))

    if not os.path.isdir(project):
        os.system('svn co svn://svn.zope.org/repos/main/%s/trunk %s' % (project, project))


