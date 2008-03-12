# A buildbot master configuration for buildout-based project repositories

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

import bsquare.status


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
    f.addStep(Compile(name="buildout",
                command='bin/buildout',
                description=['building'],
                descriptionDone=['build']))
    f.addStep(Compile(name="test",
                command='bin/test --exit-with-status',
                description=['testing'],
                descriptionDone=['tests']))

    f.treeStableTimer = 300
    return f


def configure(svn_url, http_port=8010, allowForce=False):
    """Creates a buildout master configuration.

    The configuration returned is almost functional. You just need to add
    slaves.

    """
    c = {}
    c['slavePortnum'] = 8989
    c['change_source'] = SVNPoller(svn_url, split_file=split_file, pollinterval=30)
    c['schedulers'] = [] 
    c['builders'] = []

    slow_lock = locks.SlaveLock("cpu", maxCount=2)

    projects = open("project-list.cfg", "rb").readlines()
    projects = [x.strip() for x in projects]
    for project in projects:
        f = make_factory(svn_url)
        c['builders'].append({
            'name': project,
            'slavename': 'local',
            'builddir': project,
            'factory': f,
            'locks': [slow_lock],
        })
        del f

        c['schedulers'].append(Scheduler(
            project, "%s/trunk" % project, 30, [project]))
        c['schedulers'].append(Nightly(
            "%s nightly" % project, [project], hour=[3],
            branch="%s/trunk" % project))

    # Status display(s)
    c['status'] = []
    c['status'].append(bsquare.status.ExtendedWebStatus(http_port=http_port,
                                                        allowForce=allowForce))
    return c
