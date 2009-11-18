from zope.app.zopeappgenerations import getRootFolder
from zope.app.generations.utility import findObjectsProviding
from lovely.tag.interfaces import ITaggingEngine
from BTrees import IOBTree
from zope.app.component.interfaces import ISite
def evolve(context):
    """evolve to use -IOSet- instead of -set- instances"""

    for s in findObjectsProviding(getRootFolder(context), ISite):
        for engine in s.getSiteManager().getAllUtilitiesRegisteredFor(
            ITaggingEngine):
            for key, val in engine._name_to_tagids.items():
                changed = False
                for uid in list(val):
                    if engine._tag_ids.queryObject(uid) is None:
                        changed=True
                        val.remove(uid)
                if changed or not isinstance(val, IOBTree.IOSet):
                    engine._name_to_tagids[key] = IOBTree.IOSet(val)

                
