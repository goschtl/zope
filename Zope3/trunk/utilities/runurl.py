##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""%(script)s s[options] [path] [environment variables]

    Options:

      -b username:password
      --basic username:password

         Specify a login

      -r n
      --run n

         Run the request n times without printing output

      -d file
      --database file

         Specify a database to use. The default is Data.fs in the
         current directory

      -c file
      --config file

         Specify a site configuration file to use. The default is
         site.zcml in the current directory

      -i file
      --input file

         Specify an input file to provide a request input body.

      -p file
      --profile file

         Run the profiler saving the profile data to the given file name

      -w
      --warmup

        Make one run of the URL to warm up the object caches.

      -h
      --help

         Output this usage information.
         
$Id: runurl.py,v 1.1 2003/05/02 18:28:18 jim Exp $
"""

import sys, os, getopt

def main(argv=None):
    global app, path, basic, run, stdin, env

    if argv is None:
        argv = sys.argv

    script = argv[0]
    app = _doimport(script) 
    
    args = argv[1:]

    try:
        options, args = getopt.getopt(
            args,
            'b:r:p:d:c:hi:w',
            ['basic=', 'run=', 'profile=', 'database=', 'config=', 'help',
             'input=', 'warmup'])
    except getopt.GetoptError:
        print __doc__ % {'script': script}
        raise

    
    basic = run = warm = profilef = database = config = None
    stdin = ''
    for name, value in options:
        if name in ('-b', '--basic'):
            basic = value
        elif name in ('-r', '--run'):
            run = int(value)
        elif name in ('-p', '--profile'):
            profilef = value
        elif name in ('-d', '--database'):
             database = value
        elif name in ('-c', '--config'):
             config = value
        elif name in ('-i', '--input'):
             input = value
        elif name in ('-w', '--warmup'):
             warm= True
        elif name in ('-h', '--help'):
            print __doc__ % {'script': script}
            sys.exit(0)
        else:
            print usage
            raise ValueError(name)

    path = '/'
    env = {}
    if args:
        path = args[0]
        for arg in args[1:]:
            name, value = arg.split('=', 1)
            env[name]=value

    app = app.Application(database, config)
    
    if warm:
        _mainrun(app, path, basic, 1, stdin, env)

    if profilef:
        import profile
        profile.run("_mainrun(app, path, basic, run, stdin, env)",
                    profilef)
    else:
        _mainrun(app, path, basic, run, stdin, env)
        
resultfmt = "elapsed: %.4f, cpu=%.4f, status=%s"
def _mainrun(app, path, basic, run, stdin, environment):
    if run:
        for i in range(run):
            print resultfmt %  app.run(path=path, basic=basic, stdin=stdin,
                                       environment=environment)
            
    else:
        print resultfmt % app.publish(path=path, basic=basic, stdin=stdin,
                                      environment=environment)
        

def _doimport(script):
    try:
        import zope.app
    except ImportError:
        # Get dir containing the script (utilities)
        dir = os.path.split(script)[0]
        # dir dir containing the dir containing the script (Zope3)
        dir = os.path.split(dir)[0]
        sys.path.append(os.path.join(dir, 'src'))

    from zope import app
    return app

if __name__ == "__main__":
    main()
