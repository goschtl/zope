import sys, os, subprocess, signal

def main(options):
    command = sys.argv[1]
    if command.lower() == 'start':
        args = [options['slapd'], '-f', options['conf']]
        if 'urls' in options:
            args.extend(['-h', options['urls']])
        args.extend(sys.argv[2:])
        subprocess.Popen(args)
    elif command.lower() == 'stop':
        pidfile = file(options['pidfile'])
        pid = int(pidfile.read())
        pidfile.close()
        os.kill(pid, signal.SIGTERM)
    else:
        raise ValueError('Command %s unsupported' % command)
