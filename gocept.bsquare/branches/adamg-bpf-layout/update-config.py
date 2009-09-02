#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""Update bsquare package list

$Id$
"""
import sys
import os
import subprocess

SVNBIN = 'svn'
#SSL certificate you still need to accept by 'hand'
#usually authentication will be cached by svn, in case not fill in below
SVNUSER = ''
SVNPASS = ''

is_win32 = sys.platform == 'win32'

def system(command, input=''):
    #enable for debugging
    #print command

    p = subprocess.Popen(command,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         close_fds=not is_win32)
    sts = p.wait()
    if sts != 0:
        raise OSError(
            u'An error occurred while running command: %s, error: %s' % (
                command, p.stderr.read()))
    i, o, e = (p.stdin, p.stdout, p.stderr)
    if input:
        i.write(input)
    i.close()
    result = o.read() + e.read()
    o.close()
    e.close()
    return result


def do(cmd):
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sts = os.waitpid(p.pid, 0)[1]
    if sts != 0:
        raise OSError(
            u'An error occurred while running command: %s, error: %s' % (
                cmd, p.stderr.read()))

    return p.stdout.read()

def svnls(url):
    if SVNUSER:
        svnuser = " --username %s" % SVNUSER
    else:
        svnuser = ''

    if SVNPASS:
        svnpass = " --password %s" % SVNPASS
    else:
        svnpass = ''

    return system("svn ls --non-interactive %s%s%s" % (url, svnuser, svnpass))

def main():
    if len(sys.argv) < 3:
        print "Usage: %s buildbot-config-home-dir svn-base-url" % sys.argv[0]
        sys.exit(1)

    home = sys.argv[1]
    base = sys.argv[2]

    projects = svnls(base)
    cleaned = []
    for project in projects.splitlines():
        if project.endswith('/'):
            project = project[:-1]

        try:
            svnls("%s/%s/trunk/buildout.cfg" % (base, project))
            cleaned.append(project)
        except OSError:
            pass

    open(os.path.join(home, 'project-list.cfg'), 'wb').write(
        '\n'.join(cleaned) )

    if sys.platform == 'win32':
        #there is no make usually on win32 and reconfig is also not supported
        #the only chance is to restart the win32 service
        bbservice = os.path.join(os.path.dirname(sys.executable),
                                 'scripts', 'buildbot_service.py')
        if os.path.exists(bbservice):
            system('"%s" %s restart' % (sys.executable, bbservice))
        else:
            print "Missing %s, unable to reconfig buildbot!" % bbservice
            sys.exit(1)
    else:
        #let's assume anything else is posix
        system("cd %s; make reconfig > /dev/null" % home)


if __name__ == "__main__":
    main()