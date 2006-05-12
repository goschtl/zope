import os, sys, traceback

def cvs_users(users, start, stop):
    history = os.popen(
        'cvs -d :ext:cvs.zope.org:/cvs-repository history -cal -D'+start,
        'r')
    for record in history:
        if record[0] not in 'MAR':
            continue
        action, date, time, offset, user = record.split()[:5]
        if date > stop:
            continue
        users.add(user)

def svn_users(users, start, stop):
    log = os.popen(
        'svn log -r{%s}:{%s} --xml svn+ssh://svn.zope.org/repos/main'
        % (start, stop),
        'r')
    
    for line in log:
        if '<author>' in line:
            assert '</author>' in line
            user = line.split('<author>')[1].split('</author>')[0].strip()
            users.add(user)

def user_info(users):
    info = []
    for user in users:
        record = os.popen('ssh svn.zope.org python ldump.py ' + user, 'r'
                          ).read()
        try:
            record = eval(record)[0][1]
        except:
            print "User:", user, record
            traceback.print_exc()
            continue

        info.append((
            user,
            record.get('givenName', ['(unknown)'])[0],
            record.get('sn', ['(unknown)'])[0],
            record.get('mail', ['(unknown)'])[0],
            ))
    return info

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    [start, stop] = args
    users = set()
    cvs_users(users, start, stop)
    print len(users)
    svn_users(users, start, stop)
    print len(users)
    info = sorted(user_info(users))
    info = ['\t'.join(map(lambda v: v.replace('\t', ' '), r)) for r in info]
    open('users.%s.%s.txt' % (start, stop), 'w').write('\n'.join(info)+'\n')

if __name__ == '__main__':
    main()


