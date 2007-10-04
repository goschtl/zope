from zope.interface import implements
from zope.app.container.btree import BTreeContainer
from zope.schema.fieldproperty import FieldProperty

import interfaces

class TreeNode(BTreeContainer):
    """See .interfaces.ITreeNode"""
    implements(interfaces.ITreeNode)

    title = FieldProperty(interfaces.ITreeNode['title'])

    def __init__(self, title):
        super(TreeNode, self).__init__()
        self.title = title
