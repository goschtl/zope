

def validate(issuefolder, args):
    valid = [v.strip()
             for v in open(issuefolder+'.valid').read().strip().split('\n')
             ]
    max = int(valid.pop(0))
    if len(args) > max:
        error("Too many votes.")

    seen = set()
    for arg in args:
        if arg in seen:
            error("Repeated vote: "+args)
        if arg not in valid:
            error("Invalid vote: %s.\nValid choices are: %s"
                  % (arg, ' '.join(valid))
                  )

def count(issuefolder, uname):
    vote = os.path.join(issuefolder, uname)
    if os.path.exists(vote):
        print 'You voted:'
        print open(vote).read()
    else:
        print "You haven't voted yet."
    print
    
    valid = [v.strip()
             for v in open(issuefolder+'.valid').read().strip().split('\n')
             ]
    max = int(valid.pop(0))

    print "You can make as many as %s votes from the choices:" % max
    print '\n'.join(valid)
    
    
