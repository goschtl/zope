#! /usr/bin/env python

"""
zdaemon -- run an application as a daemon.

Usage: python zdaemon.py [zdaemon-options] program [program-arguments]

Options:
  -b SECONDS -- set backoff limit to SECONDS (default 10; see below)
  -d -- run as a proper daemon; fork a background process, close files etc.
  -f -- run forever (by default, exit when the backoff limit is exceeded)
  -h -- print usage message and exit
  program [program-arguments] -- an arbitrary application to run

This daemon manager has two purposes: it restarts the application when
it dies, and (when requested to do so with the -d option) it runs the
application in the background, detached from the foreground tty
session that started it (if any).

Important: if at any point the application exits with exit status 0 or
2, it is not restarted.  Any other form of termination (either being
killed by a signal or exiting with an exit status other than 0 or 2)
causes it to be restarted.

Backoff limit: when the application exits (nearly) immediately after a
restart, the daemon manager starts slowing down by delaying between
restarts.  The delay starts at 1 second and is increased by one on
each restart up to the backoff limit given by the -b option; it is
reset when the application runs for more than the backoff limit
seconds.  By default, when the delay reaches the backoff limit, the
daemon manager exits (under the assumption that the application has a
persistent fault).  The -f (forever) option prevents this exit; use it
when you expect that a temporary external problem (such as a network
outage or an overfull disk) may prevent the application from starting
but you want the daemon manager to keep trying.

"""

"""
XXX TO DO

- Read commands from a Unix-domain socket, to stop, start and restart
  the application, and to stop the daemon manager.

"""

import os
assert os.name == "posix", "This code makes many Unix-specific assumptions"
import sys
import time
import getopt
import signal
from stat import ST_MODE

import zLOG

class Daemonizer:

    # Settable options
    daemon = 0
    forever = 0
    backofflimit = 10

    def __init__(self):
        self.filename = None
        self.args = []

    def main(self, args=None):
        self.prepare(args)
        self.run()

    def prepare(self, args=None):
        if args is None:
            args = sys.argv[1:]
        self.blather("args=%s" % repr(args))
        try:
            opts, args = getopt.getopt(args, "b:dfh")
        except getopt.error, msg:
            self.usage(str(msg))
        self.parseoptions(opts)
        self.setprogram(args)

    def parseoptions(self, opts):
        self.info("opts=%s" % repr(opts))
        for o, a in opts:
            if o == "-b":
                try:
                    self.backofflimit = float(a)
                except:
                    self.usage("invalid number: %s" % repr(a))
            if o == "-d":
                self.daemon += 1
            if o == "-f":
                self.forever += 1
            if o == "-h":
                print __doc__,
                self.exit()

    def setprogram(self, args):
        if not args:
            self.usage("missing 'program' argument")
        self.filename = self.checkcommand(args[0])
        self.args = args # A list of strings like for execvp()
        self.info("filename=%s; args=%s" %
                  (repr(self.filename), repr(self.args)))

    def checkcommand(self, command):
        if "/" in command:
            filename = command
            try:
                st = os.stat(filename)
            except os.error:
                self.usage("can't stat program %s" % repr(command))
        else:
            path = self.getpath()
            for dir in path:
                filename = os.path.join(dir, command)
                try:
                    st = os.stat(filename)
                except os.error:
                    continue
                mode = st[ST_MODE]
                if mode & 0111:
                    break
            else:
                self.usage("can't find program %s on PATH %s" %
                           (repr(command), path))
        if not os.access(filename, os.X_OK):
            self.usage("no permission to run program %s" % repr(filename))
        return filename

    def getpath(self):
        path = ["/bin", "/usr/bin", "/usr/local/bin"]
        if os.environ.has_key("PATH"):
            p = os.environ["PATH"]
            if p:
                path = p.split(os.pathsep)
        return path

    def run(self):
        self.setsignals()
        if self.daemon:
            self.daemonize()
        self.runforever()

    def setsignals(self):
        signal.signal(signal.SIGTERM, self.sigexit)
        signal.signal(signal.SIGHUP, self.sigexit)
        signal.signal(signal.SIGINT, self.sigexit)

    def sigexit(self, sig, frame):
        self.info("daemon manager killed by signal %s(%d)" %
                  (self.signame(sig), sig))
        self.exit(1)

    def daemonize(self):
        pid = os.fork()
        if pid != 0:
            # Parent
            self.blather("daemon manager forked; parent exiting")
            self.exit()
        # Child
        self.info("daemonizing the process")
        os.close(0)
        sys.stdin = sys.__stdin__ = open("/dev/null")
        os.close(1)
        sys.stdout = sys.__stdout__ = open("/dev/null", "w")
        os.close(2)
        sys.stderr = sys.__stderr__ = open("/dev/null", "w")
        os.setsid()

    def runforever(self):
        self.info("daemon manager started")
        while 1:
            self.governor()
            self.forkandexec()

    backoff = 0
    lasttime = None

    def governor(self):
        # Back off if respawning too often
        if not self.lasttime:
            pass
        elif time.time() - self.lasttime < self.backofflimit:
            # Exited rather quickly; slow down the restarts
            self.backoff += 1
            if self.backoff >= self.backofflimit:
                if self.forever:
                    self.backoff = self.backofflimit
                else:
                    self.problem("restarting too often; quit")
                    self.exit(1)
            self.info("sleep %s to avoid rapid restarts" % self.backoff)
            time.sleep(self.backoff)
        else:
            # Reset the backoff timer
            self.backoff = 0
        self.lasttime = time.time()

    def forkandexec(self):
        pid = os.fork()
        if pid != 0:
            # Parent
            self.info("forked child pid %d" % pid)
            wpid, wsts = os.waitpid(pid, 0)
            self.reportstatus(wpid, wsts)
        else:
            # Child
            self.startprogram()

    def startprogram(self):
        try:
            self.blather("about to exec %s" % self.filename)
            try:
                os.execv(self.filename, self.args)
            except os.error, err:
                self.panic("can't exec %s: %s" %
                           (repr(self.filename), str(err)))
        finally:
            os._exit(127)

    def reportstatus(self, pid, sts):
        if os.WIFEXITED(sts):
            es = os.WEXITSTATUS(sts)
            msg = "pid %d: exit status %s" % (pid, es)
            if es == 0:
                self.info(msg)
                self.exit(0)
            elif es == 2:
                self.problem(msg)
                self.exit(es)
            else:
                self.warning(msg)
        elif os.WIFSIGNALED(sts):
            signum = os.WTERMSIG(sts)
            signame = self.signame(signum)
            msg = ("pid %d: terminated by signal %s(%s)" %
                   (pid, signame, signum))
            if hasattr(os, "WCOREDUMP"):
                iscore = os.WCOREDUMP(sts)
            else:
                iscore = s & 0x80
            if iscore:
                msg += " (core dumped)"
            self.warning(msg)
        else:
            msg = "pid %d: unknown termination cause 0x%04x" % (pid, sts)
            self.warning(msg)

    signames = None

    def signame(self, sig):
        """Return the symbolic name for signal sig.

        Returns 'unknown' if there is no SIG name bound to sig in the
        signal module.
        """

        if self.signames is None:
            self.setupsignames()
        return self.signames.get(sig, "unknown")

    def setupsignames(self):
            self.signames = {}
            for k, v in signal.__dict__.items():
                startswith = getattr(k, "startswith", None)
                if startswith is None:
                    continue
                if startswith("SIG") and not startswith("SIG_"):
                    self.signames[v] = k

    # Error handling

    def usage(self, msg):
        self.problem(str(msg))
        self.errwrite("Error: %s\n" % str(msg))
        self.errwrite("For help, use zdaemon.py -h\n")
        self.exit(2)

    def errwrite(self, msg):
        sys.stderr.write(msg)

    def exit(self, sts=0):
        sys.exit(sts)

    # Log messages with various severities

    def trace(self, msg):
        self.log(msg, zLOG.TRACE)

    def debug(self, msg):
        self.log(msg, zLOG.DEBUG)

    def blather(self, msg):
        self.log(msg, zLOG.BLATHER)

    def info(self, msg):
        self.log(msg, zLOG.INFO)

    def warning(self, msg):
        self.log(msg, zLOG.WARNING)

    def problem(self, msg):
        self.log(msg, zLOG.ERROR)

    def panic(self, msg):
        self.log(msg, zLOG.PANIC)

    def getsubsystem(self):
        return "ZD:%d" % os.getpid()

    def log(self, msg, severity=zLOG.INFO):
        zLOG.LOG(self.getsubsystem(), severity, msg)

def main(args=None):
    d = Daemonizer()
    d.main(args)

if __name__ == "__main__":
    main()
