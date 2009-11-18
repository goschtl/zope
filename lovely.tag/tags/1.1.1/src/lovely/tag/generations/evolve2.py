from zope.app.zopeappgenerations import getRootFolder
from zope.app.generations.utility import findObjectsProviding
from lovely.tag.interfaces import ITaggingEngine
from BTrees import IOBTree
from zope.app.component.interfaces import ISite

def evolve(context):

    """evolve to use an IOBTree instead of PersistentList"""
    for s in findObjectsProviding(getRootFolder(context), ISite):
        for engine in s.getSiteManager().getAllUtilitiesRegisteredFor(
            ITaggingEngine):

            if hasattr(engine, '_tags'):
                engine._tagid_to_obj = IOBTree.IOBTree()
                for uid, ref in engine._tag_ids.items():
                    obj = ref()
                    engine._tagid_to_obj[uid] = obj
                del engine._tags
                del engine._tag_ids
                
