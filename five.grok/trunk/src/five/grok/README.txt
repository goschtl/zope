five.grok
=========

Overview
--------

This package is meant to provide all the grok functionalities into Zope 2.

How-to
------

This readme try to explain you how to use grok in Zope 2.

    <<< from five import grok
    <<< from OFS.ObjectManager import ObjectManager
    <<< from OFS.SimpleItem import Item

    <<< class SimpleFolder(ObjectManager, Item):
    ...     def __init__(self, id=None):
    ...         if id is not None:
    ...             self.id = str(id)

    <<< class GrokVillage(SimpleFolder):
    ...
    ...     def addCave(self, id):
    ...         cave = Cave(id)
    ...         self._setObject(id, cave)
    ...         return cave

    <<< grok.templatedir('tests/all/all_test_templates')
    <<< class GrokVillageView(grok.View):
    ...     grok.context(GrokVillage)
    ...
    ...     def getCaves(self):
    ...         cavesInfos = []
    ...         for cave in self.context.objectValues():
    ...             caveInfo = dict(id=cave.id, caveWomen=cave.numberOfCaveWomen())
    ...             cavesInfos.append(caveInfo)
    ...         return cavesInfos

    <<< class Cave(SimpleFolder):
    ...
    ...     def numberOfCaveWomen(self):
    ...         return len(self.objectIds())

    <<< class CaveView(grok.View):
    ...     grok.context(Cave)
    ...
    ...     def render(self):
    ...         return 'This is the %s cave, there is %s cavewomen in this cave.' %\
    ...                                 (self.context.id,
    ...                                  self.context.numberOfCaveWomen())

    <<< class AddCaveWoman(grok.View):
    ...     grok.context(Cave)
    ...     grok.name(u'cave-woman-add')
    ...
    ...     def render(self):
    ...         return 'Add a Cave Woman ...'
    ...
    ...     def update(self, id=None, name=None,
    ...                age=None, hairType=None, size=0,
    ...                weight=0):
    ...         self.context._setObject(id, CaveWoman(name, age, hairType,
    ...                                               size, weight))

    <<< class CaveWoman(grok.Model):
    ...
    ...     def __init__(self, name, age, hairType, size,
    ...                  weight):
    ...         self.name = name
    ...         self.age = age
    ...         self.hairType = hairType
    ...         self.size = size
    ...         self.weight = weight

    <<< from zope.interface import Interface

    <<< class ICaveWomanSummarizer(Interface):
    ...
    ...     def info():
    ...         """
    ...         return filtered informations
    ...         """

    <<< class CaveWomanFaceBookProfile(grok.Adapter):
    ...     grok.context(CaveWoman)
    ...     grok.provides(ICaveWomanSummarizer)
    ...
    ...     def info(self):
    ...         return {'hair': self.context.hairType,
    ...                 'weight': self.context.weight,
    ...                 'size': self.context.size}

    <<< from zope.app.container.interfaces import IObjectAddedEvent
    <<< from zope.component import getUtility

    <<< class ICaveInformations(Interface):
    ...
    ...     def getHairStatistics(cave):
    ...         """
    ...         return the statistics about the cavewoman's hair in the cave
    ...         """

    <<< class CaveInformations(grok.GlobalUtility):
    ...     grok.implements(ICaveInformations)
    ...     grok.provides(ICaveInformations)
    ...
    ...     def getHairStatistics(self, cave):
    ...         browns = 0
    ...         blonds = 0
    ...         for caveWoman in cave.objectValues():
    ...             if caveWoman.hairType == 'blond':
    ...                 blonds += 1
    ...             elif caveWoman.hairType == 'brown':
    ...                 browns += 1
    ...         return blonds, browns

    <<< from Acquisition import aq_parent
    <<< @grok.subscribe(CaveWoman, IObjectAddedEvent)
    ... def handle(obj, event):
    ...     profile = ICaveWomanSummarizer(obj)
    ...     caveInfos = getUtility(ICaveInformations)
    ...     village = aq_parent(obj)
    ...     nbrOfBlond, nbrOfBrown = caveInfos.getHairStatistics(village)
    ...     if nbrOfBlond >= nbrOfBrown:
    ...         obj.hairType = 'brown'
    ...     else:
    ...         obj.hairType = 'blond'
    ...     print """Hey caveman there is a new cavewoman in the cave, here
    ... are the most important informations about her:
    ...  * Hair Type: %(hair)s
    ...  * Weight: %(weight)s
    ...  * Size: %(size)s""" % profile.info()

    >>> from zope.component import getUtility
    >>> from five.grok.README import *
    >>> from Testing.ZopeTestCase import ZopeLite as Zope2
    >>> app= Zope2.app()
    >>> #grok.testing.grok(__name__)
    >>> from zope.publisher.browser import TestRequest
    >>> from OFS.Folder import Folder
    >>> request = TestRequest()
    >>> village = GrokVillage(id='amsterdam')
    >>> app._setObject('amsterdam', village)
    'amsterdam'
    >>> from zope.component import queryMultiAdapter

    >>> martijnCave = village.addCave('martijn-cave')
    >>> belgianCave = village.addCave('belgian-cave')
    >>> queryMultiAdapter((martijnCave, request), name='caveview')()
    'This is the martijn-cave cave, there is 0 cavewomen in this cave.'

    >>> queryMultiAdapter((belgianCave, request), name='caveview')()
    'This is the belgian-cave cave, there is 0 cavewomen in this cave.'

    >>> addView = queryMultiAdapter((belgianCave, request),
    ...                             name=u'cave-woman-add')

    >>> addView.update(id='emma', name='Emma', age=22,
    ...                size=160, weight=47)
    Hey caveman there is a new cavewoman in the cave, here
    are the most important informations about her:
      * Hair Type: brown
      * Weight: 47
      * Size: 160

    >>> addView.update(id='carla', name='Carla', age=23,
    ...                size=160, weight=47)
    Hey caveman there is a new cavewoman in the cave, here
    are the most important informations about her:
      * Hair Type: blond
      * Weight: 47
      * Size: 160

    >>> addView.update(id='layla', name='Layla', age=24,
    ...                size=164, weight=56)
    Hey caveman there is a new cavewoman in the cave, here
    are the most important informations about her:
      * Hair Type: brown
      * Weight: 56
      * Size: 164

    >>> addView = queryMultiAdapter((martijnCave, request),
    ...                             name=u'cave-woman-add')

    >>> addView.update(id='betty', name='Betty', age=52,
    ...                size=160, weight=90)
    Hey caveman there is a new cavewoman in the cave, here
    are the most important informations about her:
      * Hair Type: brown
      * Weight: 90
      * Size: 160

    >>> queryMultiAdapter((martijnCave, request), name='caveview')()
    'This is the martijn-cave cave, there is 1 cavewomen in this cave.'

    >>> queryMultiAdapter((belgianCave, request), name='caveview')()
    'This is the belgian-cave cave, there is 3 cavewomen in this cave.'
    >>> print queryMultiAdapter((village, request), name='grokvillageview')()
    <html>
    <body>
    <div>
    In cave martijn-cave there is 1 cavewomen.
    </div>
    <div>
    In cave belgian-cave there is 3 cavewomen.
    </div>
    </body>
    </html>
    <BLANKLINE>
