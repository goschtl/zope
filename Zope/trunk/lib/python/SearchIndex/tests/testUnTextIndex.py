##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################

import sys, os

sys.path.insert(0, os.getcwd())
try: import unittest
except:
    sys.path[0]=os.path.join(sys.path[0],'..','..')
    import unittest

class Dummy:

    def __init__(self, **kw):
        self.__dict__.update(kw)

import zLOG

def log_write(subsystem, severity, summary, detail, error):
    if severity >= zLOG.PROBLEM:
        assert 0, "%s(%s): %s" % (subsystem, severity, summary)

zLOG.log_write=log_write

import ZODB, ZODB.DemoStorage, ZODB.FileStorage
import SearchIndex.UnTextIndex
import SearchIndex.GlobbingLexicon

class Tests(unittest.TestCase):

   def setUp(self):
       self.index=SearchIndex.UnTextIndex.UnTextIndex('text')
       self.doc=Dummy(text='this is the time, when all good zopes')

   def dbopen(self):
       n = 'fs_tmp__%s' % os.getpid()
       s = ZODB.FileStorage.FileStorage(n)
       db=self.db=ZODB.DB(s)
       self.jar=db.open()
       if not self.jar.root().has_key('index'):
           self.jar.root()['index']=SearchIndex.UnTextIndex.UnTextIndex('text')
           get_transaction().commit()
       return self.jar.root()['index']

   def dbclose(self):
       self.jar.close()
       self.db.close()
       del self.jar
       del self.db

   def tearDown(self):
       get_transaction().abort()
       if hasattr(self, 'jar'):
           self.dbclose()
           os.system('rm -f fs_tmp__*')

   def checkSimpleAddDelete(self):
       "Check that we can add and delete an object without error"
       self.index.index_object(0, self.doc)
       self.index.index_object(1, self.doc)
       self.doc.text='spam is good, spam is fine, span span span'
       self.index.index_object(0, self.doc)
       self.index.unindex_object(0)

   def checkPersistentUpdate1(self):
       "Check simple persistent indexing"
       index=self.dbopen()

       self.doc.text='this is the time, when all good zopes'
       index.index_object(0, self.doc)
       get_transaction().commit()

       self.doc.text='time waits for no one'
       index.index_object(1, self.doc)
       get_transaction().commit()
       self.dbclose()

       index=self.dbopen()
       
       r = index._apply_index({})
       assert r==None

       r = index._apply_index({'text': 'python'})
       assert len(r) == 2 and r[1]==('text',), 'incorrectly not used'
       assert not r[0], "should have no results"
               
       r = index._apply_index({'text': 'time'})
       r=list(r[0].keys())
       assert  r == [0,1], r

   def checkPersistentUpdate2(self):
       "Check less simple persistent indexing"
       index=self.dbopen()

       self.doc.text='this is the time, when all good zopes'
       index.index_object(0, self.doc)
       get_transaction().commit()

       self.doc.text='time waits for no one'
       index.index_object(1, self.doc)
       get_transaction().commit()

       self.doc.text='the next task is to test'
       index.index_object(3, self.doc)
       get_transaction().commit()

       self.doc.text='time time'
       index.index_object(2, self.doc)
       get_transaction().commit()
       self.dbclose()

       index=self.dbopen()
       
       r = index._apply_index({})
       assert r==None

       r = index._apply_index({'text': 'python'})
       assert len(r) == 2 and r[1]==('text',), 'incorrectly not used'
       assert not r[0], "should have no results"
               
       r = index._apply_index({'text': 'time'})
       r=list(r[0].keys())
       assert  r == [0,1,2], r



   sample_texts = [
       """This is the time for all good men to come to
       the aid of their country""",
       """ask not what your country can do for you,
       ask what you can do for your country""",
       """Man, I can't wait to get to Montross!""",
       """Zope Public License (ZPL) Version 1.0""",
       """Copyright (c) Digital Creations.  All rights reserved.""",
       """This license has been certified as Open Source(tm).""",
       """I hope I get to work on time""",
       ]
       
   def checkGlobQuery(self):
       "Check a glob query"
       index=self.dbopen()
       index._lexicon = SearchIndex.GlobbingLexicon.GlobbingLexicon()

       for i in range(len(self.sample_texts)):
           self.doc.text=self.sample_texts[i]
           index.index_object(i, self.doc)
           get_transaction().commit()

       self.dbclose()

       index=self.dbopen()

       r = index._apply_index({'text':'m*n'})
       r=list(r[0].keys())
       assert  r == [0,2], r

   def checkAndQuery(self):
       "Check an AND query"
       index=self.dbopen()
       index._lexicon = SearchIndex.GlobbingLexicon.GlobbingLexicon()

       for i in range(len(self.sample_texts)):
           self.doc.text=self.sample_texts[i]
           index.index_object(i, self.doc)
           get_transaction().commit()

       self.dbclose()

       index=self.dbopen()

       r = index._apply_index({'text':'time and country'})
       r=list(r[0].keys())
       assert  r == [0,], r

   def checkOrQuery(self):
       "Check an OR query"
       index=self.dbopen()
       index._lexicon = SearchIndex.GlobbingLexicon.GlobbingLexicon()

       for i in range(len(self.sample_texts)):
           self.doc.text=self.sample_texts[i]
           index.index_object(i, self.doc)
           get_transaction().commit()

       self.dbclose()

       index=self.dbopen()

       r = index._apply_index({'text':'time or country'})
       r=list(r[0].keys())
       assert  r == [0,1,6], r

def test_suite():
   return unittest.makeSuite(Tests, 'check')

def main():
   unittest.TextTestRunner().run(test_suite())

def debug():
   test_suite().debug()

def pdebug():
    import pdb
    pdb.run('debug()')
   
if __name__=='__main__':
   if len(sys.argv) > 1:
      globals()[sys.argv[1]]()
   else:
      main()

