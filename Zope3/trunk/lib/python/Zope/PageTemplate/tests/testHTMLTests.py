##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
import os, sys, unittest

from Zope.PageTemplate.tests import util
from Zope.PageTemplate.PageTemplate import PageTemplate


class Folder:
   context = property(lambda self: self)

class HTMLTests(unittest.TestCase):

   def setUp(self):
      self.folder = f = Folder()
      f.laf = PageTemplate()
      f.t = PageTemplate()

   def getProducts(self):
      return [
         {'description': 'This is the tee for those who LOVE Zope. '
          'Show your heart on your tee.',
          'price': 12.99, 'image': 'smlatee.jpg'
          },
         {'description': 'This is the tee for Jim Fulton. '
          'He\'s the Zope Pope!',
          'price': 11.99, 'image': 'smpztee.jpg'
          },
         ]

   def check1(self):
      laf = self.folder.laf
      laf.write(util.read_input('TeeShopLAF.html'))
      expect = util.read_output('TeeShopLAF.html')
      util.check_html(expect, laf())

   def check2(self):
      self.folder.laf.write(util.read_input('TeeShopLAF.html'))

      t = self.folder.t
      t.write(util.read_input('TeeShop2.html'))
      expect = util.read_output('TeeShop2.html')
      out = t(laf = self.folder.laf, getProducts = self.getProducts)
      util.check_html(expect, out)
      

   def check3(self):
      self.folder.laf.write(util.read_input('TeeShopLAF.html'))

      t = self.folder.t
      t.write(util.read_input('TeeShop1.html'))
      expect = util.read_output('TeeShop1.html')
      out = t(laf = self.folder.laf, getProducts = self.getProducts)
      util.check_html(expect, out)

   def checkSimpleLoop(self):
      t = self.folder.t
      t.write(util.read_input('Loop1.html'))
      expect = util.read_output('Loop1.html')
      out = t()
      util.check_html(expect, out)

   def checkGlobalsShadowLocals(self):
      t = self.folder.t
      t.write(util.read_input('GlobalsShadowLocals.html'))
      expect = util.read_output('GlobalsShadowLocals.html')
      out = t()
      util.check_html(expect, out)

   def checkStringExpressions(self):
      t = self.folder.t
      t.write(util.read_input('StringExpression.html'))
      expect = util.read_output('StringExpression.html')
      out = t()
      util.check_html(expect, out)
      
   def checkReplaceWithNothing(self):
      t = self.folder.t
      t.write(util.read_input('CheckNothing.html'))
      expect = util.read_output('CheckNothing.html')
      out = t()
      util.check_html(expect, out)

   def checkWithXMLHeader(self):
      t = self.folder.t
      t.write(util.read_input('CheckWithXMLHeader.html'))
      expect = util.read_output('CheckWithXMLHeader.html')
      out = t()
      util.check_html(expect, out)

   def checkNotExpression(self):
      t = self.folder.t
      t.write(util.read_input('CheckNotExpression.html'))
      expect = util.read_output('CheckNotExpression.html')
      out = t()
      util.check_html(expect, out)
      
   def checkPathNothing(self):
      t = self.folder.t
      t.write(util.read_input('CheckPathNothing.html'))
      expect = util.read_output('CheckPathNothing.html')
      out = t()
      util.check_html(expect, out)
      
   def checkPathAlt(self):
      t = self.folder.t
      t.write(util.read_input('CheckPathAlt.html'))
      expect = util.read_output('CheckPathAlt.html')
      out = t()
      util.check_html(expect, out)


def test_suite():
   return unittest.makeSuite(HTMLTests, 'check')

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
