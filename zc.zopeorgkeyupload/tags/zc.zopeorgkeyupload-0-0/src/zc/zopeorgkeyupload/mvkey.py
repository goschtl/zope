import os
import pwd
import re
import sys

iskey = re.compile('-[12]$').search


valid_groups = 'zopesvn', 'cvsusers'

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    try:
        [keydir, users] = args
    except:
        print 'Usage: %s key-drop-dir user-list-file' % sys.argv[0]
        sys.exit(1)
        
    users = set(open(users).read().strip().split())
    
    for name in os.listdir(keydir):
        if iskey(name):
            keypath = os.path.join(keydir, name)
            login, type_ = name.rsplit('-', 1)
            try:
                uid, gid, c, home = pwd.getpwnam(login)[2:6]
            except KeyError:
                print 'Invalid login', login
                os.remove(keypath)
                continue

            if uid < 100 or gid < 100:
                print 'Hack? System account', login
                os.remove(keypath)
                continue

            if login not in users:
                print 'Hack? Not in a valid user', login
                os.remove(keypath)
                continue

            sshdir = os.path.join(home, '.ssh')
            if not os.path.exists(sshdir):
                os.mkdir(sshdir)
                os.chown(sshdir, uid, gid)
                os.chmod(sshdir, 0755)
            
            if type_ == '1':
                dest = 'authorized_keys'
            else:
                dest = 'authorized_keys2'

            dest = os.path.join(sshdir, dest)
            os.chown(keypath, uid, gid)
            os.chmod(keypath, 0755)
            os.rename(keypath, dest)
