#!python
##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""zdctl -- control an application run by zdaemon.

Usage: python zdctl.py [-C URL] [-h] [-p PROGRAM]
       [zdrun-options] [action [arguments]]

Options:
-C/--configuration URL -- configuration file or URL
-h/--help -- print usage message and exit
-b/--backoff-limit SECONDS -- set backoff limit to SECONDS (default 10)
-d/--daemon-- run as a proper daemon; fork a subprocess, close files etc.
-f/--forever -- run forever (by default, exit when backoff limit is exceeded)
-h/--help -- print this usage message and exit
-i/--interactive -- start an interactive shell after executing commands
-l/--logfile -- log file to be read by logtail command
-p/--program PROGRAM -- the program to run
-s/--socket-name SOCKET -- Unix socket name for client (default "zdsock")
-u/--user USER -- run as this user (or numeric uid)
-x/--exit-codes LIST -- list of fatal exit codes (default "0,2")
-z/--directory DIRECTORY -- directory to chdir to when using -d (default "/")
action [arguments] -- see below

Actions are commands like "start", "stop" and "status".  If -i is
specified or no action is specified on the command line, a "shell"
interpreting actions typed interactively is started (unless the
configuration option default_to_interactive is set to false).  Use the
action "help" to find out about available actions.
"""

from __future__ import nested_scopes

# XXX Related code lives in lib/python/Zope/Startup/ZctlLib.py on the
# 'chrism-install-branch' branch.
# The code there knows more about Zope and about Windows, but doesn't
# use zdaemon.py or ZConfig.

import os
import re
import cmd
import sys
import time
import signal
import socket

if __name__ == "__main__":
    # Add the parent of the script directory to the module search path
    # (but only when the script is run from inside the zdaemon package)
    from os.path import dirname, basename, abspath, normpath
    scriptdir = dirname(normpath(abspath(sys.argv[0])))
    if basename(scriptdir).lower() == "zdaemon":
        sys.path.append(dirname(scriptdir))

import ZConfig
from zdaemon.zdoptions import RunnerOptions


def string_list(arg):
    return arg.split()


class ZDCtlOptions(RunnerOptions):

    positional_args_allowed = 1

    def __init__(self):
        RunnerOptions.__init__(self)
        self.add("interactive", None, "i", "interactive", flag=1)
        self.add("default_to_interactive", "runner.default_to_interactive",
                 default=1)
        self.add("program", "runner.program", "p:", "program=",
                 handler=string_list,
                 required="no program specified; use -p or -C")
        self.add("logfile", "runner.logfile", "l:", "logfile=")
        self.add("python", "runner.python")
        self.add("zdrun", "runner.zdrun")

    def realize(self, *args, **kwds):
        RunnerOptions.realize(self, *args, **kwds)

        # Maybe the config file requires -i or positional args
        if not self.args and not self.interactive:
            if not self.default_to_interactive:
                self.usage("either -i or an action argument is required")
            self.interactive = 1

        # Where's python?
        if not self.python:
            self.python = sys.executable

        # Where's zdrun?
        if not self.zdrun:
            if __name__ == "__main__":
                file = sys.argv[0]
            else:
                file = __file__
            file = os.path.normpath(os.path.abspath(file))
            dir = os.path.dirname(file)
            self.zdrun = os.path.join(dir, "zdrun.py")


class ZDCmd(cmd.Cmd):

    prompt = "zdctl> "

    def __init__(self, options):
        self.options = options
        cmd.Cmd.__init__(self)
        self.get_status()
        if self.zd_status:
            m = re.search("(?m)^args=(.*)$", self.zd_status)
            if m:
                s = m.group(1)
                args = eval(s, {"__builtins__": {}})
                if args != self.options.program:
                    print "WARNING! zdrun is managing a different program!"
                    print "our program   =", self.options.program
                    print "daemon's args =", args

    def emptyline(self):
        pass # We don't want a blank line to repeat the last command

    def send_action(self, action):
        """Send an action to the zdrun server and return the response.

        Return None if the server is not up or any other error happened.
        """
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(self.options.sockname)
            sock.send(action + "\n")
            sock.shutdown(1) # We're not writing any more
            response = ""
            while 1:
                data = sock.recv(1000)
                if not data:
                    break
                response += data
            sock.close()
            return response
        except socket.error, msg:
            return None

    def get_status(self):
        self.zd_up = 0
        self.zd_pid = 0
        self.zd_status = None
        resp = self.send_action("status")
        if not resp:
            return
        m = re.search("(?m)^application=(\d+)$", resp)
        if not m:
            return
        self.zd_up = 1
        self.zd_pid = int(m.group(1))
        self.zd_status = resp

    def awhile(self, cond, msg):
        try:
            self.get_status()
            while not cond():
                sys.stdout.write(". ")
                sys.stdout.flush()
                time.sleep(1)
                self.get_status()
        except KeyboardInterrupt:
            print "^C"
        else:
            print msg % self.__dict__

    def help_help(self):
        print "help          -- Print a list of available actions."
        print "help <action> -- Print help for <action>."

    def do_EOF(self, arg):
        print
        return 1

    def do_start(self, arg):
        self.get_status()
        if not self.zd_up:
            args = [
                self.options.python,
                self.options.zdrun,
                ]
            args += self._get_override("-C", "configfile")
            args += self._get_override("-b", "backofflimit")
            args += self._get_override("-d", "daemon", flag=1)
            args += self._get_override("-f", "forever", flag=1)
            args += self._get_override("-s", "sockname")
            args += self._get_override("-u", "user")
            args += self._get_override("-x", "exitcodes",
                                       ",".join(map(str, self.options.exitcodes)))
            args += self._get_override("-z", "directory")
            args.extend(self.options.program)
            if self.options.daemon:
                flag = os.P_WAIT
            else:
                flag = os.P_NOWAIT
            os.spawnvp(flag, args[0], args)
        elif not self.zd_pid:
            self.send_action("start")
        else:
            print "daemon process already running; pid=%d" % self.zd_pid
            return
        self.awhile(lambda: self.zd_pid,
                    "daemon process started, pid=%(zd_pid)d")

    def _get_override(self, opt, name, svalue=None, flag=0):
        value = getattr(self.options, name)
        if value is None:
            return []
        configroot = self.options.configroot
        if configroot is not None:
            for n, cn in self.options.names_list:
                if n == name and cn:
                    v = configroot
                    for p in cn.split("."):
                        v = getattr(v, p, None)
                        if v is None:
                            break
                    if v == value: # We didn't override anything
                        return []
                    break
        args = [opt]
        if not flag:
            if svalue is None:
                svalue = str(value)
            args.append(svalue)
        return args
                        

    def help_start(self):
        print "start -- Start the daemon process."
        print "         If it is already running, do nothing."

    def do_stop(self, arg):
        self.get_status()
        if not self.zd_up:
            print "daemon manager not running"
        elif not self.zd_pid:
            print "daemon process not running"
        else:
            self.send_action("stop")
            self.awhile(lambda: not self.zd_pid, "daemon process stopped")

    def help_stop(self):
        print "stop -- Stop the daemon process."
        print "        If it is not running, do nothing."

    def do_restart(self, arg):
        self.get_status()
        pid = self.zd_pid
        if not pid:
            self.do_start(arg)
        else:
            self.send_action("restart")
            self.awhile(lambda: self.zd_pid not in (0, pid),
                        "daemon process restarted, pid=%(zd_pid)d")

    def help_restart(self):
        print "restart -- Stop and then start the daemon process."

    def do_kill(self, arg):
        if not arg:
            sig = signal.SIGTERM
        else:
            try:
                sig = int(arg)
            except: # int() can raise any number of exceptions
                print "invalid signal number", `arg`
                return
        self.get_status()
        if not self.zd_pid:
            print "daemon process not running"
            return
        print "kill(%d, %d)" % (self.zd_pid, sig)
        try:
            os.kill(self.zd_pid, sig)
        except os.error, msg:
            print "Error:", msg
        else:
            print "signal %d sent to process %d" % (sig, self.zd_pid)

    def help_kill(self):
        print "kill [sig] -- Send signal sig to the daemon process."
        print "              The default signal is SIGTERM."

    def do_wait(self, arg):
        self.awhile(lambda: not self.zd_pid, "daemon process stopped")
        self.do_status()

    def help_wait(self):
        print "wait -- Wait for the daemon process to exit."

    def do_status(self, arg=""):
        if arg not in ["", "-l"]:
            print "status argument must be absent or -l"
            return
        self.get_status()
        if not self.zd_up:
            print "daemon manager not running"
        elif not self.zd_pid:
            print "daemon manager running; daemon process not running"
        else:
            print "program running; pid=%d" % self.zd_pid
        if arg == "-l" and self.zd_status:
            print self.zd_status

    def help_status(self):
        print "status [-l] -- Print status for the daemon process."
        print "               With -l, show raw status output as well."

    def do_show(self, arg):
        if not arg:
            arg = "options"
        try:
            method = getattr(self, "show_" + arg)
        except AttributeError, err:
            print err
            self.help_show()
            return
        method()

    def show_options(self):
        print "zdctl/zdrun options:"
        print "schemafile:  ", repr(self.options.schemafile)
        print "configfile:  ", repr(self.options.configfile)
        print "interactive: ", repr(self.options.interactive)
        print "default_to_interactive:",
        print                  repr(self.options.default_to_interactive)
        print "zdrun:       ", repr(self.options.zdrun)
        print "python:      ", repr(self.options.python)
        print "program:     ", repr(self.options.program)
        print "backofflimit:", repr(self.options.backofflimit)
        print "forever:     ", repr(self.options.forever)
        print "sockname:    ", repr(self.options.sockname)
        print "exitcodes:   ", repr(self.options.exitcodes)
        print "user:        ", repr(self.options.user)
        print "directory:   ", repr(self.options.directory)
        print "logfile:     ", repr(self.options.logfile)
        print "hang_around: ", repr(self.options.hang_around)

    def show_python(self):
        print "Python info:"
        version = sys.version.replace("\n", "\n              ")
        print "Version:     ", version
        print "Platform:    ", sys.platform
        print "Executable:  ", repr(sys.executable)
        print "Arguments:   ", repr(sys.argv)
        print "Directory:   ", repr(os.getcwd())
        print "Path:"
        for dir in sys.path:
            print "    " + repr(dir)

    def show_all(self):
        self.show_options()
        print
        self.show_python()

    def help_show(self):
        print "show options -- show zdctl options"
        print "show python -- show Python version and details"
        print "show all -- show all of the above"

    def complete_show(self, text, *ignored):
        options = ["options", "python", "all"]
        return [x for x in options if x.startswith(text)]

    def do_logreopen(self, arg):
        self.do_kill(str(signal.SIGUSR2))

    def help_logreopen(self):
        print "logreopen -- Send a SIGUSR2 signal to the daemon process."
        print "             This is designed to reopen the log file."

    def do_logtail(self, arg):
        if not arg:
            arg = self.options.logfile
            if not arg:
                print "No default log file specified; use -l or -C"
                return
        try:
            os.system("tail -f %s" % arg)
        except KeyboardInterrupt:
            print

    def help_logtail(self):
        print "logtail [logfile] -- Run tail -f on the given logfile."
        print "                     A default file may exist."
        print "                     Hit ^C to exit this mode."

    def do_quit(self, arg):
        self.get_status()
        if not self.zd_up:
            print "daemon manager not running"
        elif not self.zd_pid:
            print "daemon process not running; stopping daemon manager"
            self.send_action("exit")
            self.awhile(lambda: not self.zd_up, "daemon manager stopped")
        else:
            print "daemon process and daemon manager still running"
        return 1

    def help_quit(self):
        print "quit -- Exit the zdctl shell."
        print ("        If the daemon process is not running, "
               "stop the daemon manager.")

def main(args=None):
    options = ZDCtlOptions()
    options.realize(args)
    c = ZDCmd(options)
    if options.args:
        c.onecmd(" ".join(options.args))
    if options.interactive:
        try:
            import readline
        except ImportError:
            pass
        print "program:", " ".join(options.program)
        c.do_status()
        c.cmdloop()

if __name__ == "__main__":
    main()
