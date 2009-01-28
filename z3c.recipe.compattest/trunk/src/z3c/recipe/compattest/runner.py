import subprocess
import sys
import os.path

def main(*scripts):
    failed = dict()

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

