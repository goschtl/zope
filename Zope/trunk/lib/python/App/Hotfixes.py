
from version_txt import getZopeVersion
from zLOG import LOG, INFO, WARNING

merged_hotfixes = {
    'Hotfix_2001-09-28': 1
    }


APPLY = 1
ALREADY_MERGED = 0
OUTDATED_ZOPE = None


def isMerged(name):
    return merged_hotfixes.get(name, 0)


def logHotfix(id, apply_hotfix):
    if apply_hotfix:
        LOG('Hotfixes', INFO, 'Applying %s' % id)
    elif apply_hotfix is OUTDATED_ZOPE:
        LOG('Hotfixes', WARNING, 'Not applying %s.  It is not designed for '
            'this version of Zope.  Please uninstall the hotfix product.'
            % id)
    else:  # ALREADY_MERGED
        LOG('Hotfixes', WARNING, 'Not applying %s.  The fix has already been '
            'merged into Zope.  Please uninstall the hotfix product.'
            % id)


def beforeApplyHotfix(id, req_major, req_minor, req_micro):
    major, minor, micro = getZopeVersion()[:3]
    if major > 0 and (
        (major * 10000 + minor * 100 + micro) <
        (req_major * 10000 + req_minor * 100 + req_micro)):
        # The version of Zope is too old for this hotfix.
        apply_hotfix = OUTDATED_ZOPE
    elif isMerged(id):
        apply_hotfix = ALREADY_MERGED
    else:
        apply_hotfix = APPLY
    logHotfix(id, apply_hotfix)
    return apply_hotfix

