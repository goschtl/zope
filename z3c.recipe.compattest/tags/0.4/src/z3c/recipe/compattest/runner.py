import StringIO
import os.path
import select
import subprocess
import sys


def usage():
    print """
usage: %s [OPTIONS]

All given options will be passed to each test runner. To know which
options you can use, refer to the test runner documentation.
""" % sys.argv[0]

class Job(object):

    def __init__(self, script, args):
        self.script = script
        self.args = args
        self.name = os.path.basename(script)
        self.output = StringIO.StringIO()
        self.exitcode = None

    def start(self):
        self.process = subprocess.Popen(
            [self.script, '--exit-with-status'] + self.args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            close_fds=True)

    def poll(self):
        self.exitcode = self.process.poll()
        read, _, _ = select.select([self.process.stdout], [], [], 0.01)
        if read:
            self.output.write(read[0].read())


def main(max_jobs, *scripts):
    argv = sys.argv[1:]
    if '-h' in argv or '--help' in argv:
        usage()
        return

    running = []
    completed = []
    scripts = list(scripts)

    while scripts or running:
        for job in running:
            job.poll()
            if job.exitcode is None:
                continue
            completed.append(job)
            running.remove(job)
            if job.exitcode:
                print "%s failed with:" % job.name
                print job.output.getvalue()

        while (len(running) < max_jobs) and scripts:
            script = scripts.pop(0)
            job = Job(script, sys.argv[1:])
            print "Running %s" % job.name
            job.start()
            running.append(job)

    failures = [job for job in completed if job.exitcode]
    print "%d failure(s)." % len(failures)
    for job in failures:
        print "-", job.name
