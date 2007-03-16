##############################################################################
#
# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

_upgrade_registry = {} # id -> step

class UpgradeStep(object):
    """A step to upgrade a component.
    """
    def __init__(self, title, profile, source, dest, handler,
                 checker=None, sortkey=0):
        self.id = str(abs(hash('%s%s%s%s' % (title, source, dest, sortkey))))
        self.title = title
        if source == '*':
            source = None
        elif isinstance(source, basestring):
            source = tuple(source.split('.'))
        self.source = source
        if dest == '*':
            dest = None
        elif isinstance(dest, basestring):
            dest = tuple(dest.split('.'))
        self.dest = dest
        self.handler = handler
        self.checker = checker
        self.sortkey = sortkey
        self.profile = profile

    def versionMatch(self, portal, source):
        return (source is None or
                self.source is None or
                source <= self.source)

    def isProposed(self, portal, source):
        """Check if a step can be applied.

        False means already applied or does not apply.
        True means can be applied.
        """
        checker = self.checker
        if checker is None:
            return self.versionMatch(portal, source)
        else:
            return checker(portal)

    def doStep(self, portal):
        self.handler(portal)

def _registerUpgradeStep(step):
    _upgrade_registry[step.id] = step

def listUpgradeSteps(portal, source):
    """Lists upgrade steps available from a given version.
    """
    res = []
    for id, step in _upgrade_registry.items():
        proposed = step.isProposed(portal, source)
        if (not proposed
            and source is not None
            and (step.source is None or source > step.source)):
            continue
        info = {
            'id': id,
            'step': step,
            'title': step.title,
            'source': step.source,
            'dest': step.dest,
            'proposed': proposed,
            }
        res.append(((step.source or '', step.sortkey, proposed), info))
    res.sort()
    res = [i[1] for i in res]
    return res
