##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

# This is a fake functional test
# The problem was that zope.testbrowser is working against the publisher
# and liveserver is working on the twisted/WSGI level
# solution is:
# - bring up the complete server (at the moment manually)
# - issue requests against this server
# - liveserver does not write to the ZODB --> no need to clear it
#
# We have two goals:
# - functional testing
# - benchmarking
#   - total request time will be taken

import os
import sys
import re
import time
import urllib
import urllib2
import unittest
from base64 import encodestring

from zope.testbrowser.browser import Browser
from zope.testbrowser.browser import PystoneTimer

from threading import Thread

BASEURL = 'http://localhost:8088/@@livecomments.html'
INURL = BASEURL+'/@@input/%(uuid)s'
OUTURL = BASEURL+'/@@output/%(uuid)s'
UID_EXTRACT = re.compile(r"LivePage.uuid = '(\w*?)'")

#manager user
USER = "adi"
PWD = "r"

ROUNDUP = 3
TIMEOUT = 30

"""
[00:00.000 - client 127.0.0.1:3114 forwarded to localhost:8088]
POST /@@livecomments.html/@@input/0000010a79a60c576aa49f2600c000a80000000d HTTP/1.1
Host: localhost:8089
User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.0.1) Gecko/20060111 Firefox/1.5.0.1
Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5
Accept-Language: en-us,en;q=0.5
Accept-Encoding: gzip,deflate
Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7
Keep-Alive: 300
Connection: close
X-Requested-With: XMLHttpRequest
X-Prototype-Version: 1.4.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 62
Pragma: no-cache
Cache-Control: no-cache

&name=update&id=text3&html=%3Cp%3Edx%3C%2Fp%3E&extra=scroll&_=

http://localhost:8089/@@livecomments.html

<script type="text/javascript">LivePage.uuid = '0000010a79a60c576aa49f2600c000a80000000d';</script>
"""

class Data(dict, object):
	u"""neat dictionary wrapper"""

	def __init__(self, **kw):
		self.update(kw)

	def __getattr__(self, name):
		return self[name]

	def __setattr__(self, name, value):
		self[name] = value


class Timer:
    def __init__(self):
        self.timer = PystoneTimer()
    
    def _start_timer(self):
        self.timer.start()

    def _stop_timer(self):
        self.timer.stop()
    
    @property
    def lastRequestPystones(self):
        return self.timer.elapsedPystones

    @property
    def lastRequestSeconds(self):
        return self.timer.elapsedSeconds
    
    getElapsed = lastRequestPystones

def timePrinter(msg, timelist):
    """average, max, min time calculator, printer """
    total = sum(timelist)
    avg = round(total/len(timelist), ROUNDUP)
    high = round(max(timelist), ROUNDUP)
    low = round(min(timelist), ROUNDUP)
    
    print msg, 'avg:',avg,'max:',high,'min:',low

def getAuth(usr, pwd):
    auth = "Basic %s" % encodestring("%s:%s" % (usr, pwd)
                                 ).replace("\012", "")
    return auth

def sleep(secs):
    for i in range(secs,0,-1):
        print i,
        time.sleep(1)
    print ''

def getUid(browser):
    browser.open(BASEURL)
    
    uid = UID_EXTRACT.search(browser.contents,re.S)
    return uid.group(1)

class testUtils(object):
    def makeTimer(self):
        self.timer = Timer()
    
    def getUid(self):
        self.uid = getUid(Browser())

    def inputRequest(self, url, strg, timelist, uid=None, postdata=None):
        """simulate INPUT request
        request is blocking
        """
        if postdata:
            data=postdata
            wiredata = urllib.urlencode(data)
        elif strg:
            data={'name':'update',
                'id':'text',
                'html':strg,
                'extra':'scroll',
                '_':''}
            wiredata = urllib.urlencode(data)
        else:
            wiredata = None
        
        if uid is None:
            uid = self.uid
        wireurl = url % {'uuid':uid}
        
        print '-->',strg
        self.timer._start_timer()
        result = urllib2.urlopen(wireurl, wiredata)
        self.timer._stop_timer()
        
        #print self.timer.getElapsed
        
        timelist.append(self.timer.getElapsed)
        
        #'ok'
        return result.read()
    
    def outputRequest(self, url, browser, timelist, uid=None):
        """simulate OUTPUT request
        request is blocking
        collect timing in timelist
        """
        if uid is None:
            uid = self.uid
        wireurl = url % {'uuid':uid}
        
        #print wireurl
        
        self.timer._start_timer()
        browser.open(wireurl)
        self.timer._stop_timer()
        
        #print self.timer.getElapsed
        
        timelist.append(self.timer.getElapsed)
        
        return browser.contents
    
    def getOutput(self, browser, timelist, uid=None):
        """issue OUTPUT request
        get data from OUTPUT result
        """
        print '<--'
        
        x=self.outputRequest(OUTURL, browser, timelist, uid)
        
        #simulating the delay of the javascript
        time.sleep(0.5)
        
        null=None #for eval
        retval=eval(x)
        #print retval
        
        return retval
    
    def getOnlyTextOutput(self, browser, timelist, uid=None):
        """issue OUTPUT request
        get data from OUTPUT result
        loop requests until 'id'=='text'
        """
        while True:
            retval = self.getOutput(browser, timelist, uid)
            
            if retval.get('id','') == 'text':
                print retval['html']
                return retval

######################################################################
######################################################################

class liveserverTest(testUtils, unittest.TestCase):
    def setUp(self):
        self.makeTimer()
        self.getUid()
        
    def test_weird(self):
        """test weird request values
        
        """
        ##invalid uid, wrong url
        outputb = Browser()
        url = BASEURL+'/@@out/%(uuid)s'
        wireurl = url % {'uuid':self.uid}
        try:
            outputb.open(wireurl)
            
            print outputb.contents
            
            self.fail("Should be a 404 Not found")
        except urllib2.HTTPError, e:
            self.assertEqual(e.code, 404)
        
        #invalid uid, input
        inputb = Browser()
        wireurl = INURL % {'uuid':'123invalid'}
        try:
            inputb.open(wireurl)

            print inputb.contents
            
            self.fail("Should be a 400 Bad Request")
        except urllib2.HTTPError, e:
            self.assertEqual(e.code, 400)
        
        #uid OK, invalid data?
        data={'name':'update',
            'id':'text',
            'html':'<p>any</p>',
            'extra':'scroll',
            'invalid':'invalid',
            '_':''}
        print self.inputRequest(INURL, '', [], self.uid, data)
        #TODO: no error: is this OK?
        
        data={'kickit':''}
        try:
            print self.inputRequest(INURL, '', [], self.uid, data)
            
            self.fail("Should be a 400 Bad Request")
        except urllib2.HTTPError, e:
            self.assertEqual(e.code, 400)
        
        data={'name':'update',
            'id':'invalid',
            'html':'<p>any</p>',
            'extra':'scroll',
            '_':''}
        print self.inputRequest(INURL, '', [], self.uid, data)
        #TODO: no error: is this OK?
        
        data={'name':'invalid',
            'id':'text',
            'html':'<p>any</p>',
            'extra':'scroll',
            '_':''}
        try:
            print self.inputRequest(INURL, '', [], self.uid, data)
            
            self.fail("Should be a 400 Bad Request")
        except urllib2.HTTPError, e:
            self.assertEqual(e.code, 400)
        
        data={'name':'text',
            'id':'text',
            'html':'<p>any</p>',
            'extra':'invalid',
            '_':''}
        try:
            print self.inputRequest(INURL, '', [], self.uid, data)
            
            self.fail("Should be a 400 Bad Request")
        except urllib2.HTTPError, e:
            self.assertEqual(e.code, 400)
        
        #uid OK, what about DOS attack -- XXL data
        #if I hit the memory limit of the server, then it's REAL slow
        #although server restart/shutdown is still possible
        data={'name':'update',
            'id':'text',
            'html':'<p>any</p>'*10000000,
            'extra':'scroll',
            '_':''}
        try:
            print self.inputRequest(INURL, '', [], self.uid, data)
            
            self.fail("Should be a 400 Bad Request")
        except urllib2.HTTPError, e:
            self.assertEqual(e.code, 400)
        
        #invalid uid, output
        outputb = Browser()
        wireurl = OUTURL % {'uuid':'123invalid'}
        try:
            outputb.open(wireurl)
            
            print outputb.contents
            
            self.fail("Should be a 400 Bad Request")
        except urllib2.HTTPError, e:
            self.assertEqual(e.code, 400)
    
    def xtest_noevent(self):
        """test_noevent
        test for:
        client makes an input
        queries events x times
        
        result should be:
        first response: input comes back
        any following responses: after <TIMEOUT> second timeout, 'idle' message"""
        
        strg = '<p>any</p>'
        
        self.inputRequest(INURL, strg, [])
        
        outputb = Browser()
        
        retval = self.getOnlyTextOutput(outputb, [])
        self.assertEqual(retval['html'], strg)
        
        for i in range(2):
            #self.timer._start_timer()
            retval = self.getOutput(outputb, [])
            #print retval
            #self.timer._stop_timer()
            
            self.assert_(self.timer.lastRequestSeconds>TIMEOUT)
            self.assertEqual(retval['name'], 'idle')
    
    def xtest_timeout(self):
        """test_timeout
        test for:
        client makes an input
        wait <TIMEOUT+5> secs
        
        result should be:
        first response: input comes back
        next response: reload
        """
        strg = '<p>any</p>'
        
        self.inputRequest(INURL, strg, [])
        
        outputb = Browser()
        
        retval = self.getOnlyTextOutput(outputb, [])
        self.assertEqual(retval['html'], strg)
        
        sleep(TIMEOUT+5)
        
        retval=self.getOutput(outputb, [])
        self.assertEqual(retval['name'], 'reload')
    
    def xtest_getInput(self):
        """test_getInput
        Creativity rules: issue a GET against @@input instead of POST
        """
        inputb = Browser()
        url = INURL
        wireurl = url % {'uuid':self.uid}
        try:
            inputb.open(wireurl)
            
            self.fail("Should be a 400 Bad Request")
        except urllib2.HTTPError, e:
            self.assertEqual(e.code, 400)

        #check for "400 Bad Request"
    
    def xtest_retval(self):
        """test_retval
        test for:
        client makes an input
        same client queries, check for the same output text as the input
        
        result should be:
        input comes back
        """
        
        values = ['s','st','star','star is','star','start','started','o','over']
        outputb = Browser()
        
        for v in values:
            self.inputRequest(INURL, v, [])
            
            retval = self.getOnlyTextOutput(outputb, [])
            self.assertEqual(retval['html'], v)
    
    def checktwo(self, text, brw1, uid1, brw2, uid2):
        """check the output text of two users """
        retval = self.getOnlyTextOutput(brw1, [], uid1)
        self.assertEqual(retval['html'], text)
        
        retval = self.getOnlyTextOutput(brw2, [], uid2)
        self.assertEqual(retval['html'], text)
    
    def xtest_twoUsersListening(self):
        """test_twoUsersListening
        one user is typing,
        two users listening for texts
        the two users have to get the typed text"""
        values = ['s','st','star','star is','star','start','started','o','over']
        outputb1 = Browser()
        uid1 = self.uid
        outputb2 = Browser()
        outputb2.addHeader('Authorization', getAuth(USER, PWD))
        uid2 = getUid(outputb2)
        
        for v in values:
            self.inputRequest(INURL, v, [], uid1)
            
            self.checktwo(v, outputb1, uid1, outputb2, uid2)
    
    def xtest_twoUsersTyping(self):
        """test_twoUsersTyping
        two users inputting text,
        two listening for texts"""
        values1 = ['s','st','star','star is','star','start','started','o','over']
        #9
        values2 = ['c','cra','crazy','cra','crater','c','hover']
        #7
        #total 16
        order = [1,2,1,2,1,1,2,2,1,2,2,1,1,2,1,1]
        #
        self.assertEqual(len(values1)+len(values2), len(order))
        self.assertEqual(len(values1), order.count(1))
        self.assertEqual(len(values2), order.count(2))
        #sanity check
        
        outputb1 = Browser()
        uid1 = self.uid
        outputb2 = Browser()
        outputb2.addHeader('Authorization', getAuth(USER, PWD))
        uid2 = getUid(outputb2)
        
        p1=0
        p2=0
        for o in order:
            if o==1:
                inuid = uid1
                v = values1[p1]
                p1+=1
            else:
                inuid = uid2
                v = values2[p2]
                p2+=1
            
            self.inputRequest(INURL, v, [], inuid)
            
            self.checktwo(v, outputb1, uid1, outputb2, uid2)
    
    def xtest_onlineUsers(self):
        """test_onlineUsers
        two users, checking for online status
        here we behave nicely as expected
        
        user1=unauthenticated
        user2=manager"""
        
        timestamp = Timer()
        
        #wait for all to timeout
        #to have a clear picture
        sleep(TIMEOUT+5)
        
        outputb1 = Browser()
        uid1 = getUid(outputb1)
        outputb2 = Browser()
        outputb2.addHeader('Authorization', getAuth(USER, PWD))
        uid2 = getUid(outputb2)
        
        #
        #retval=self.getOutput(outputb1, [], uid1)
        #print retval
        #self.assertEqual(retval['name'], 'reload')
        ##reload it
        #uid1 = getUid(outputb1)
        #
        #retval=self.getOutput(outputb2, [], uid2)
        #print retval
        #self.assertEqual(retval['name'], 'reload')
        ##reload it
        #uid2 = getUid(outputb2)
        
        #fake input
        #the reload has to put the two online
        
        timestamp._start_timer()
        
        self.inputRequest(INURL, 'x1', [], uid1)
        self.inputRequest(INURL, 'x2', [], uid2)
        
        print '--- user 1'
        
        #print timestamp.lastRequestSeconds
        
        retval=self.getOutput(outputb1, [], uid1)
        print retval
        self.assertEqual(retval['name'], 'update')
        self.assertEqual(retval['id'], 'online')
        self.assertEqual(retval['html'], 'Unauthenticated User, Manager')
        
        #print timestamp.lastRequestSeconds
        
        retval=self.getOutput(outputb1, [], uid1)
        print retval
        self.assertEqual(retval['id'], 'text')
        ##is it coming back really in order?
        self.assertEqual(retval['html'], 'x1')
        
        #print timestamp.lastRequestSeconds
        
        retval=self.getOutput(outputb1, [], uid1)
        print retval
        self.assertEqual(retval['id'], 'text')
        ##is it coming back really in order?
        self.assertEqual(retval['html'], 'x2')
        
        print '--- user 2'
        
        #print timestamp.lastRequestSeconds
        
        retval=self.getOutput(outputb2, [], uid2)
        print retval
        self.assertEqual(retval['name'], 'update')
        self.assertEqual(retval['id'], 'online')
        self.assertEqual(retval['html'], 'Unauthenticated User, Manager')
        
        #print timestamp.lastRequestSeconds
        
        retval=self.getOutput(outputb2, [], uid2)
        print retval
        self.assertEqual(retval['id'], 'text')
        ##is it coming back really in order?
        self.assertEqual(retval['html'], 'x1')
        
        #print timestamp.lastRequestSeconds
        
        retval=self.getOutput(outputb2, [], uid2)
        print retval
        self.assertEqual(retval['id'], 'text')
        ##is it coming back really in order?
        self.assertEqual(retval['html'], 'x2')
        
        #print timestamp.lastRequestSeconds
        
        #TODO: ??? that should be an idle??? but is online: Manager
        retval=self.getOutput(outputb2, [], uid2)
        print retval
        self.assertEqual(retval['name'], 'idle')
        
        #print timestamp.lastRequestSeconds
        
        #retval=self.getOutput(outputb2, [], uid2)
        #print retval
        
        #print timestamp.lastRequestSeconds
    
    def xtest_onlineUsersReconnect(self):
        """test_onlineUsersReconnect
        two users, checking for online status
        Getting dirty: simulating that the users get disconnected and send
        again INPUT instead of doing a reload
        
        user1=unauthenticated
        user2=manager"""
        outputb1 = Browser()
        uid1 = getUid(outputb1)
        outputb2 = Browser()
        outputb2.addHeader('Authorization', getAuth(USER, PWD))
        uid2 = getUid(outputb2)
        
        #wait for all to timeout
        sleep(TIMEOUT+5)
        
        #fake input to put the two online
        self.inputRequest(INURL, 'x1', [], uid1)
        self.inputRequest(INURL, 'x2', [], uid2)
        
        print '--- user 1'
        
        retval=self.getOutput(outputb1, [], uid1)
        print retval
        self.assertEqual(retval['name'], 'reload')
        
        uid1 = getUid(outputb1)
        
        retval=self.getOutput(outputb1, [], uid1)
        print retval
        self.assertEqual(retval['name'], 'idle')
        
        #self.assertEqual(retval['id'], 'online')
        #self.assertEqual(retval['html'], 'Unauthenticated User')
        
        print '--- user 2'
        
        retval=self.getOutput(outputb2, [], uid2)
        print retval
        self.assertEqual(retval['name'], 'reload')
        
        uid2 = getUid(outputb2)
        
        retval=self.getOutput(outputb2, [], uid2)
        print retval
        self.assertEqual(retval['name'], 'idle')

class liveserverBenchmark(testUtils, unittest.TestCase):
    def setUp(self):
        self.makeTimer()
        self.getUid()
    
    def oneinout(self, strg, inputtimes, outputtimes):
        self.inputRequest(INURL, strg, inputtimes)
        
        outputb = Browser()
        #outputb.addHeader('Authorization', getAuth(USER, PWD))
        retval = self.getOnlyTextOutput(outputb, outputtimes)
        
        print (retval['html'] == strg)
        
    def test_multi(self):
        inputtimes = []
        outputtimes = []

        for i in range(100):
            self.oneinout('<p>benchmarking</p>', inputtimes, outputtimes)
        
        timePrinter('input', inputtimes)
        timePrinter('output',outputtimes)


#test_noevent()

#test_timeout()

#test_multi()

#test_retval()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(liveserverTest))
    #suite.addTest(unittest.makeSuite(liveserverBenchmark))
    return suite

SOFTWARE_HOME = r"Y:\zope\svn_zope3\src"
INSTANCE_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CONFIG_FILE = os.path.join(INSTANCE_HOME, "etc", "zope.conf")


def start_zope():
    if sys.version_info < ( 2,3,5 ):
        print """\
        ERROR: Your python version is not supported by Zope3.
        Zope3 needs Python 2.3.5 or greater. You are running:""" + sys.version
        sys.exit(1)

    # This removes the script directory from sys.path, which we do
    # since there are no modules here.
    #
    basepath = filter(None, sys.path)

    sys.path[:] = [os.path.join(INSTANCE_HOME, "lib", "python"),
                   SOFTWARE_HOME] + basepath

    from zope.app.twisted.main import main
    main(["-C", CONFIG_FILE] + sys.argv[1:])


if __name__ == '__main__':
    #start_zope()
    
    evto = os.getenv('LIVESERVER_TIMEOUT')
    if evto:
        try:
            TIMEOUT = int(evto)
        except:
            pass

    unittest.main(defaultTest='test_suite',argv=sys.argv+['-v'])
