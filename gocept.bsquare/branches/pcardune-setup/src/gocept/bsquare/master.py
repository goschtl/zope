# A buildbot master configuration for buildout-based project repositories

import sys
import os.path
import subprocess
from twisted.python import log

from buildbot import locks

from buildbot.changes.svnpoller import SVNPoller, split_file_branches
from buildbot.steps.source import SVN
from buildbot.steps.shell import Compile
from buildbot.process.factory import BuildFactory

from buildbot.process.base import Build
from buildbot.status import html
from buildbot.scheduler import Scheduler, Nightly

from gocept.bsquare import status

is_win32 = sys.platform == 'win32'

def split_file(path):
    pieces = path.split("/")
    if len(pieces) < 2:
        return None
    project, branch = pieces[0], pieces[1]
    if branch != "trunk":
        return None
    return ("%s/%s" % (project, branch), "/".join(pieces[2:]))


def make_factory(svn_url):
    f = BuildFactory()
    f.addStep(SVN(baseURL=svn_url, mode='clobber'))
    f.addStep(Compile(name='bootstrap',
                command='buildout bootstrap .',
                description=['bootstrapping'],
                descriptionDone=['bootstrap']))
    if is_win32:
        command = "bin\\buildout.exe"
    else:
        command = 'bin/buildout'
    f.addStep(Compile(name="buildout",
                command=command,
                description=['building'],
                descriptionDone=['build']))
    if is_win32:
        command = "bin\\test.exe --exit-with-status -1"
    else:
        command = 'bin/test --exit-with-status -1' #-1 == stop on first error
    f.addStep(Compile(name="test",
                command=command,
                description=['testing'],
                descriptionDone=['tests']))

    f.treeStableTimer = 300
    return f


def configure(svn_url, http_port=8010, allowForce=False,
              svnuser = None, svnpasswd = None,
              pollinterval = 30, nightlyhour=3,
              poller = None, makefactory = make_factory,
              maxConcurrent = 2,
              svnbin = 'svn'):
    """Creates a buildout master configuration.

    The configuration returned is almost functional. You just need to add
    slaves.

    Options are as follows:
    * svn_url: URL of the SVN repository
    * http_port: where buildbot will listen as an HTTP server
    * allowForce: allow force builds (True/False)
    * svnuser: username to be passed to svn
    * svnpasswd: password to be passed to svn
    * pollinterval: interval in seconds to poll the svn repo for changes
    * nightlyhour: run nightly builds at this hour
    * poller: custom poller object instance to be used instead of SVNPoller
    * makefactory:
      * can a simple callable factory that gets the svn_url
      * can be a dict of factories getting svn_url keyed by project name
        * ``__default__`` is a special key, bsquare reverts to this factory
          first when there is none for a project
        * bsquare reverts to make_factory as last
    * maxConcurrent: maximum number of concurrent builds
    * svnbin: passed directly to SVNPoller (win32 seems to be picky about
                                            svn location)

    """
    c = {}
    c['slavePortnum'] = 8989
    if poller is None:
        c['change_source'] = SVNPoller(svn_url,
                                       split_file=split_file,
                                       svnuser=svnuser,
                                       svnpasswd=svnpasswd,
                                       pollinterval=pollinterval,
                                       svnbin=svnbin)
    else:
        c['change_source'] = poller
    c['schedulers'] = []
    c['builders'] = []

    slow_lock = locks.SlaveLock("cpu", maxCount=maxConcurrent)

    projects = open("project-list.cfg", "rb").readlines()
    projects = [x.strip() for x in projects]

    for project in projects:
        if isinstance(make_factory, dict):
            f = makefactory.get(project,
                                makefactory.get('__default__', make_factory))
            f = f(svn_url)
        else:
            f = makefactory(svn_url)
        c['builders'].append({
            'name': project,
            'slavename': 'local',
            'builddir': project,
            'factory': f,
            'locks': [slow_lock],
        })
        del f

        c['schedulers'].append(Scheduler(
            project, "%s/trunk" % project, pollinterval+10, [project]))
        c['schedulers'].append(Nightly(
            "%s nightly" % project, [project], hour=[nightlyhour],
            branch="%s/trunk" % project))

    # Status display(s)
    c['status'] = []
    c['status'].append(status.ExtendedWebStatus(http_port=http_port,
                                                allowForce=allowForce))
    return c
