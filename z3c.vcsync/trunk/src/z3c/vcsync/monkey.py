
def apply_monkey_patches():
    """Apply all monkey-patches
    """
    svn_r_status_support()

def svn_r_status_support():
    """monkey-patch py 0.9.1 with support for SVN 'R' status flag.

    this should be fixed in py 0.9.2, so the monkey patch should go
    away when we start using that.
    """
    from py.__.path.svn import wccommand
    wccommand.WCStatus.attrnames = wccommand.WCStatus.attrnames + ('replaced',)
    wccommand.SvnWCCommandPath.status = status

from py.__.path.svn.wccommand import WCStatus

# taken from py.path.svn.wccommand
def status(self, updates=0, rec=0, externals=0):
    """ return (collective) Status object for this file. """
    # http://svnbook.red-bean.com/book.html#svn-ch-3-sect-4.3.1
    #             2201     2192        jum   test
    # XXX
    if externals:
        raise ValueError("XXX cannot perform status() "
                         "on external items yet")
    else:
        #1.2 supports: externals = '--ignore-externals'
        externals = ''
    if rec:
        rec= ''
    else:
        rec = '--non-recursive'

    # XXX does not work on all subversion versions
    #if not externals: 
    #    externals = '--ignore-externals' 

    if updates:
        updates = '-u'
    else:
        updates = ''

    update_rev = None

    cmd = 'status -v %s %s %s' % (updates, rec, externals)
    out = self._authsvn(cmd)
    rootstatus = WCStatus(self)
    for line in out.split('\n'):
        if not line.strip():
            continue
        #print "processing %r" % line
        flags, rest = line[:8], line[8:]
        # first column
        c0,c1,c2,c3,c4,c5,x6,c7 = flags
        #if '*' in line:
        #    print "flags", repr(flags), "rest", repr(rest)

        if c0 in '?XI':
            fn = line.split(None, 1)[1]
            if c0 == '?':
                wcpath = self.join(fn, abs=1)
                rootstatus.unknown.append(wcpath)
            elif c0 == 'X':
                wcpath = self.__class__(self.localpath.join(fn, abs=1),
                                        auth=self.auth)
                rootstatus.external.append(wcpath)
            elif c0 == 'I':
                wcpath = self.join(fn, abs=1)
                rootstatus.ignored.append(wcpath)

            continue

        #elif c0 in '~!' or c4 == 'S':
        #    raise NotImplementedError("received flag %r" % c0)

        m = self._rex_status.match(rest)
        if not m:
            if c7 == '*':
                fn = rest.strip()
                wcpath = self.join(fn, abs=1)
                rootstatus.update_available.append(wcpath)
                continue
            if line.lower().find('against revision:')!=-1:
                update_rev = int(rest.split(':')[1].strip())
                continue
            # keep trying
            raise ValueError, "could not parse line %r" % line
        else:
            rev, modrev, author, fn = m.groups()
        wcpath = self.join(fn, abs=1)
        #assert wcpath.check()
        if c0 == 'M':
            assert wcpath.check(file=1), "didn't expect a directory with changed content here"
            rootstatus.modified.append(wcpath)
        elif c0 == 'A' or c3 == '+' :
            rootstatus.added.append(wcpath)
        elif c0 == 'D':
            rootstatus.deleted.append(wcpath)
        elif c0 == 'C':
            rootstatus.conflict.append(wcpath)
        # XXX following two lines added by monkey-patch
        elif c0 == 'R':
            rootstatus.replaced.append(wcpath)
        elif c0 == '~':
            rootstatus.kindmismatch.append(wcpath)
        elif c0 == '!':
            rootstatus.incomplete.append(wcpath)
        elif not c0.strip():
            rootstatus.unchanged.append(wcpath)
        else:
            raise NotImplementedError("received flag %r" % c0)

        if c1 == 'M':
            rootstatus.prop_modified.append(wcpath)
        # XXX do we cover all client versions here?
        if c2 == 'L' or c5 == 'K':
            rootstatus.locked.append(wcpath)
        if c7 == '*':
            rootstatus.update_available.append(wcpath)

        if wcpath == self:
            rootstatus.rev = rev
            rootstatus.modrev = modrev
            rootstatus.author = author
            if update_rev:
                rootstatus.update_rev = update_rev
            continue
    return rootstatus
