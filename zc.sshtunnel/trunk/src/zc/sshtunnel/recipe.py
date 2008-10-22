##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""\
`zc.buildout` recipe to create and manage an SSH tunnel using an rc script.

"""
__docformat__ = "reStructuredText"

import os


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.name = name
        self.options = options

        self.via = options["via"]
        self.specification = options["specification"]
        parts = self.specification.split(":")
        wait_port = int(parts[-3])
        self.wait_port = str(wait_port)

        python = options.get("python", "buildout")
        self.executable = buildout[python]["executable"]

        self.script = os.path.join(
            buildout["buildout"]["bin-directory"], name)
        self.pidfile = os.path.join(
            buildout["buildout"]["parts-directory"], name + ".pid")

        options["executable"] = self.executable
        options["pidfile"] = self.pidfile
        options["run-script"] = self.script

    def install(self):
        d = {
            "name": self.name,
            "pid_file": self.pidfile,
            "python": self.executable,
            "specification": self.specification,
            "via": self.via,
            "wait_port": self.wait_port,
            }
        text = tunnel_script_template % d
        f = open(self.script, "w")
        f.write(text)
        f.close()
        os.chmod(self.script, int("0770", 8))
        return [self.script]

    def update(self):
        # No changes, so nothing to do.
        pass


tunnel_script_template = r"""#!%(python)s

import os, sys, signal, socket, time, errno

pid_file = "%(pid_file)s"
specification = "%(specification)s"
via = "%(via)s"
wait_port = %(wait_port)s
name = "%(name)s"

def wait(port):
    addr = 'localhost', port
    for i in range(120):
        time.sleep(0.25)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(addr)
            s.close()
            break
        except socket.error, e:
            if e[0] not in (errno.ECONNREFUSED, errno.ECONNRESET):
                raise
            s.close()
    else:
        raise

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    [verb] = args

    if verb == 'start':
        if os.path.exists(pid_file):
            print "Pid file %%s already exists" %% pid_file
            return

        pid = os.fork()
        if pid == 0:
            # redirect output to /dev/null.  This will
            # cause nohup to be unannoying
            os.dup2(os.open('/dev/null', os.O_WRONLY), 1)
            os.dup2(os.open('/dev/null', os.O_WRONLY), 2)
            pid = os.spawnlp(os.P_NOWAIT, 'nohup', 'nohup',
                             'ssh', '-TnaxqNL'+specification,  via)
            open(pid_file, 'w').write("%%s\n" %% pid)
        else:
            wait(wait_port)
            print name, 'started'
    elif verb == 'fg':
        if os.path.exists(pid_file):
            print "Pid file %s already exists" % pid_file
            return
        os.execlp('ssh', 'ssh', '-TnaxqNL'+specification, via)
    elif verb == 'status':
        if os.path.exists(pid_file):
            pid = int(open(pid_file).read().strip())
            try:
                os.kill(pid, 0)
            except OSError, v:
                if v.errno == errno.ESRCH:
                    print name, 'not running'
                    # Unlink the pid_file if we can, to avoid having
                    # process numbers cycle around and accidentally
                    # recognizing some other process mistakenly.
                    try:
                        os.unlink(pid_file)
                    except OSError:
                        pass
                else:
                    print v
            else:
                print name, 'running'
        else:
            print "Pid file %%s doesn't exist" %% pid_file
    elif verb == 'stop':
        if os.path.exists(pid_file):
            pid = int(open(pid_file).read().strip())
            try:
                os.kill(pid, signal.SIGINT)
            except OSError, v:
                print v
            os.remove(pid_file)
            print name, 'stopped'
        else:
            print "Pid file %%s doesn't exist" %% pid_file
    elif verb == 'restart':
        main(['stop'])
        main(['start'])
        return
    else:
        raise ValueError("Unknown verb", verb)

if __name__ == '__main__':
    main()
"""
