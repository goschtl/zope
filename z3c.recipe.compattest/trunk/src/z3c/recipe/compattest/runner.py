import subprocess
import sys
import os.path

def usage():
    print """
usage: %s [OPTIONS]

All given options will be passed to each test runner. To know which
options you can use, refer to the test runner documentation.
""" % sys.argv[0]

def main(*scripts):
    failed = dict()
    argv = sys.argv[1:]
    if '-h' in argv or '--help' in argv:
        usage()
        return

    for script in scripts:
        print "Running %s" % os.path.basename(script)
        p = subprocess.Popen(
            [script, '--exit-with-status'] + sys.argv[1:],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            close_fds=True)
        p.wait()
        if p.returncode:
            failed[script] = p.stdout.read()
            print "Failed with:"
            print failed[script]

    print "%d failures.%s" % (
        len(failed), '\n- '.join(failed.keys()))

