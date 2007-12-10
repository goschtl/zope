import sys, os, subprocess, signal

def main(options):
    command = sys.argv[1]
    if command.lower() == 'start':
        args = [options['slapd'], '-f', options['conf']]
        if 'urls' in options:
            args.extend(['-h', options['urls']])
        args.extend(sys.argv[2:])
        subprocess.Popen(args)
        while not os.path.exists(options['pidfile']):
            pass
    elif command.lower() == 'stop':
        pidfile = file(options['pidfile'])
        pid = int(pidfile.read())
        pidfile.close()
        os.kill(pid, signal.SIGTERM)
        while os.path.exists(options['pidfile']):
            pass
    else:
        raise ValueError('Command %s unsupported' % command)
