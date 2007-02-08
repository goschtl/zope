import grok
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager

class Model(SimpleItem, grok.Model):
    pass

class Application(ObjectManager, grok.Model):
    pass
