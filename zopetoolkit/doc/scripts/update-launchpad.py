from launchpadlib.launchpad import Launchpad, EDGE_SERVICE_ROOT
from launchpadlib.credentials import Credentials
import os
import os.path

ZTK = os.path.expanduser(os.path.join('~', '.ztk'))
CACHEDIR = os.path.join(ZTK, 'cache')
CREDENTIALS = os.path.join(ZTK, 'credentials')

if not os.path.exists(ZTK):
    os.mkdir(ZTK)

try:
    credentials = Credentials()
    credentials.load(open(CREDENTIALS))
    launchpad = Launchpad(credentials, EDGE_SERVICE_ROOT, CACHEDIR)
except:
    launchpad = Launchpad.get_token_and_login(
        'ZTK helper tools', EDGE_SERVICE_ROOT, CACHEDIR)
    launchpad.credentials.save(open(CREDENTIALS, 'w'))

ztk_group = launchpad.project_groups['zopetoolkit']

# XXX Currently needs a file 'packages' that reflects which packages we
# manage.
for project in open('packages'):
    project = project.strip()
    print project, 
    try:
        project = launchpad.projects[project]
    except KeyError:
        project = launchpad.projects.new_project(
            display_name=project,
            home_page_url='http://pypi.python.org/pypi/%s' % project,
            name=project,
            summary='XXX Fill in',
            title=project)
        print "created",

    # Ensure project group is ztk
    print "Updating project data"
    project.project_group_link = ztk_group
    project.licenses = [u'Zope Public License']
    project.programming_language = 'Python'
    try:
        project.lp_save()
    except:
        print "\tfailed"
        continue
