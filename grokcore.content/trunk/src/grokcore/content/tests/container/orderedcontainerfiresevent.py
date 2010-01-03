"""
Mind that there is a subscriber to the containermodified event in order to
illustrate an ordered container fires events just like normal containers::

  >>> from grokcore.component import testing
  >>> testing.grok(__name__)
  >>> bones = OrderedBones()

Add an item::

  >>> bones['thigh'] = Bone('Thigh Bone')
  Container has changed!

Now change the order::

  >>> bones.updateOrder(order=['thigh'])
  Container has changed!

Delete an item::

  >>> del bones['thigh']
  Container has changed!
  >>> bones.keys()
  []

"""

from grokcore.component import subscribe
from grokcore.content import Model, OrderedContainer
from zope.container.interfaces import IContainerModifiedEvent

class OrderedBones(OrderedContainer):
    pass

class Bone(Model):
    def __init__(self, name):
        self.name = name

@subscribe(OrderedBones, IContainerModifiedEvent)
def container_changed(object, event):
    print 'Container has changed!'
