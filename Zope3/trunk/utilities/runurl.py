##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
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

      --hotshot file

         Run the hotshot profiler saving the profile data to the given
         file name

      -w
      --warmup

        Make one run of the URL to warm up the object caches.

      -h
      --help

         Output this usage information.

      --build

        Run from a build directory

$Id$
"""

import sys, os, getopt, gc

def main(argv=None):
    global app, path, basic, run, stdin, env, debugger

    if argv is None:
        argv = sys.argv

    script = argv[0]

    args = argv[1:]

    try:
        options, args = getopt.getopt(
            args,
            'b:r:p:d:c:hi:w',
            ['basic=', 'run=', 'profile=', 'database=', 'config=', 'help',
             'input=', 'warmup', 'build', 'hotshot='])
    except getopt.GetoptError:
        print __doc__ % {'script': script}
        raise


    basic = run = warm = profilef = database = config = hotshotf = None
    stdin = ''
    src = 'src'
    for name, value in options:
        if name in ('-b', '--basic'):
            basic = value
        elif name in ('-r', '--run'):
            run = int(value)
        elif name in ('-p', '--profile'):
            profilef = value
        elif name in ('--hotshot', ):
            hotshotf = value
        elif name in ('--build', ):
            from distutils.util import get_platform
            PLAT_SPEC = "%s-%s" % (get_platform(), sys.version[0:3])
            src = os.path.join("build", "lib.%s" % PLAT_SPEC)

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

    src = os.path.abspath(src)

    path = '/'
    env = {}
    if args:
        path = args[0]
        for arg in args[1:]:
            name, value = arg.split('=', 1)
            env[name]=value

    app = _doimport(script, src)
    from zope.app.debug import Debugger
    debugger = Debugger(database, config)

    if warm:
        _mainrun(debugger, path, basic, 1, stdin, env)

    if profilef or hotshotf:
        cmd = "_mainrun(debugger, path, basic, run, stdin, env, True)"
        if profilef:
            import profile
            profile.run(cmd, profilef)
        if hotshotf:
            import hotshot
            p = hotshot.Profile(hotshotf)
            p.runctx(cmd, globals(), locals())
            p.close()
            del p

            print 'Writing', hotshotf
            from hotshot.stats import StatsLoader
            p = StatsLoader(hotshotf).load()
            import marshal
            marshal.dump(p.stats, open(hotshotf, 'w'))
            print 'Wrote', hotshotf

    else:
        _mainrun(debugger, path, basic, run, stdin, env)

resultfmt = "elapsed: %.4f, cpu=%.4f, status=%s"
def _mainrun(debugger, path, basic, run, stdin, environment, profile=False):
    if profile:
        threshold = gc.get_threshold()
        gc.disable()
    if run:
        es = []
        cs = []
        for i in range(run):
            e, c, status = debugger.run(path=path, basic=basic, stdin=stdin,
                                        environment=environment)
            es.append(e)
            cs.append(c)
            if profile:
                collect()
            print resultfmt % (e, c, status)

        if run > 1:
            print "min elapsted: %.4f, min cpu=%.4f" % (min(es), min(cs))
            es.sort()
            cs.sort()
            e = (es[(run+1)/2-1]+es[(run+2)/2-1]) / 2.0
            c = (cs[(run+1)/2-1]+cs[(run+2)/2-1]) / 2.0
            print "med elapsted: %.4f, med cpu=%.4f" % (e, c)
    else:
        print resultfmt % debugger.publish(path=path, basic=basic, stdin=stdin,
                                           environment=environment)
    if profile:
        gc.set_threshold(*threshold)
        gc.enable()


def collect():
    #gc.collect()
    gc.enable()
    gc.set_threshold(1)
    l = [1]
    l = l * 10
    l = None
    gc.disable()
    

def _doimport(script, src):
    try:
        import zope.app
    except ImportError:
        # Get dir containing the script (utilities)
        dir = os.path.split(script)[0]
        # dir dir containing the dir containing the script (Zope3)
        dir = os.path.split(dir)[0]
        sys.path.append(os.path.join(dir, src))

    from zope import app
    return app

if __name__ == "__main__":
    main()
