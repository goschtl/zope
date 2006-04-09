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
from pub.dbgpclient import brk

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

x="""
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

from threading import *
import copy

class Future:

    def __init__(self,func,*param):
        # Constructor
        self.__done=0
        self.__result=None
        self.__status='working'
        self.__excpt = None

        self.__C=Condition()   # Notify on this Condition when result is ready

        # Run the actual function in a separate thread
        self.__T=Thread(target=self.Wrapper,args=(func,param))
        self.__T.setName("FutureThread")
        self.__T.start()

    def __repr__(self):
        return '<Future at '+hex(id(self))+':'+self.__status+'>'

    def __call__(self):
        # an exception was thrown in the thread, re-raise it here.
        if self.__excpt:
            raise self.__excpt[0], self.__excpt[1], self.__excpt[2]
        
        self.__C.acquire()
        while self.__done==0:
            self.__C.wait()
        self.__C.release()
        # We deepcopy __result to prevent accidental tampering with it.
        a=copy.deepcopy(self.__result)
        return a
    
    def isDone(self):
        return self.__done

    def Wrapper(self, func, param):
        # Run the actual function, and let us housekeep around it
        self.__C.acquire()
        try:
            self.__result=func(*param)
        except:
            self.__excpt = sys.exc_info()
            self.__result="Unknown exception raised within Future"
        self.__done=1
        self.__status=`self.__result`
        self.__C.notify()
        self.__C.release()

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

    def inputRequest(self, url, strg, timelist, uid=None):
        """simulate INPUT request
        request is blocking
        """
        if strg:
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

class liveserverTest(testUtils, unittest.TestCase):
    def setUp(self):
        self.makeTimer()
        self.getUid()
        
    def test_noevent(self):
        """test for:
        client makes an input
        queries events x times
        
        result should be:
        first response: input comes back
        any following responses: after <TIMEOUT> second timeout, 'idle' message"""
        
        strg = '<p>any</p>'
        
        self.inputRequest(INURL, strg, [])
        
        outputb = Browser()
        
        retval = self.getOnlyTextOutput(outputb, [])
        self.assert_(retval['html'] == strg)
        
        for i in range(3):
            #self.timer._start_timer()
            retval = self.getOutput(outputb, [])
            print retval
            #self.timer._stop_timer()
            
            self.assert_(self.timer.lastRequestSeconds>TIMEOUT)
            self.assert_(retval['name']=='idle')
    
    def xtest_timeout(self):
        """test for:
        client makes an input
        wait <TIMEOUT+5> secs
        
        result should be:
        first response: input comes back
        any following responses: ???
        """
        strg = '<p>any</p>'
        
        self.inputRequest(INURL, strg, [])
        
        outputb = Browser()
        
        retval = self.getOnlyTextOutput(outputb, [])
        self.assert_(retval['html'] == strg)
        
        sleep(TIMEOUT+5)
        
        retval=self.getOutput(outputb, [])
        self.assert_(retval['name']=='reload')
        
        #TODO: seems to fail?
    
    def test_retval(self):
        """test for:
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
            self.assert_(retval['html'] == v)
    
    def checktwo(self, text, brw1, uid1, brw2, uid2):
        """check the output text of two users """
        retval = self.getOnlyTextOutput(brw1, [], uid1)
        self.assert_(retval['html'] == text)
        
        retval = self.getOnlyTextOutput(brw2, [], uid2)
        self.assert_(retval['html'] == text)
    
    def test_twoUsersListening(self):
        """one user is typing,
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
    
    def test_twoUsersTyping(self):
        """two users inputting text,
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
    
    def test_onlineUsers(self):
        """two users, checking for online status
        here we behave nicely as expected
        
        user1=unauthenticated
        user2=manager"""
        
        timestamp = Timer()
        
        outputb1 = Browser()
        uid1 = getUid(outputb1)
        outputb2 = Browser()
        outputb2.addHeader('Authorization', getAuth(USER, PWD))
        uid2 = getUid(outputb2)
        
        #wait for all to timeout
        #to have a clear picture
        #sleep(TIMEOUT+5)
        
        #retval=self.getOutput(outputb1, [], uid1)
        #print retval
        #self.assert_(retval['name'] == 'reload')
        ##reload it
        #uid1 = getUid(outputb1)
        #
        #retval=self.getOutput(outputb2, [], uid2)
        #print retval
        #self.assert_(retval['name'] == 'reload')
        ##reload it
        #uid2 = getUid(outputb2)
        
        #fake input
        #the reload has to put the two online
        
        timestamp._start_timer()
        
        self.inputRequest(INURL, 'x1', [], uid1)
        self.inputRequest(INURL, 'x2', [], uid2)
        
        print '--- user 1'
        
        print timestamp.lastRequestSeconds
        
        retval=self.getOutput(outputb1, [], uid1)
        print retval
        #self.assert_(retval['name'] == 'update')
        #self.assert_(retval['id'] == 'online')
        #self.assert_(retval['html'] == 'Unauthenticated User')
        
        print timestamp.lastRequestSeconds
        
        retval=self.getOutput(outputb1, [], uid1)
        print retval
        #self.assert_(retval['id'] == 'text')
        ##is it coming back really in order?
        #self.assert_(retval['html'] == 'x1')
        
        print timestamp.lastRequestSeconds
        
        retval=self.getOutput(outputb1, [], uid1)
        print retval
        #self.assert_(retval['id'] == 'text')
        ##is it coming back really in order?
        #self.assert_(retval['html'] == 'x2')
        
        print '--- user 2'
        
        print timestamp.lastRequestSeconds
        
        retval=self.getOutput(outputb2, [], uid2)
        print retval
        
        print timestamp.lastRequestSeconds
        
        retval=self.getOutput(outputb2, [], uid2)
        print retval
        
        print timestamp.lastRequestSeconds
        
        retval=self.getOutput(outputb2, [], uid2)
        print retval
        
        print timestamp.lastRequestSeconds
        
        retval=self.getOutput(outputb2, [], uid2)
        print retval
        
        print timestamp.lastRequestSeconds
        
        retval=self.getOutput(outputb2, [], uid2)
        print retval
        
        print timestamp.lastRequestSeconds
    
    def test_onlineUsersReconnect(self):
        """two users, checking for online status
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
        self.assert_(retval['name'] == 'reload')
        
        uid1 = getUid(outputb1)
        
        retval=self.getOutput(outputb1, [], uid1)
        print retval
        self.assert_(retval['name'] == 'idle')
        
        #self.assert_(retval['id'] == 'online')
        #self.assert_(retval['html'] == 'Unauthenticated User')
        
        print '--- user 2'
        
        retval=self.getOutput(outputb2, [], uid2)
        print retval
        self.assert_(retval['name'] == 'reload')
        
        uid2 = getUid(outputb2)
        
        retval=self.getOutput(outputb2, [], uid2)
        print retval
        self.assert_(retval['name'] == 'idle')

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

#def tt(name):
#    #brw=Browser()
#    #util = testUtils()
#    #util.makeTimer()
#    #util.getUid()
#    
#    x=liveserverTest(methodName='test_retval')
#    x.setUp()
#    while True:
#        #util.inputRequest(INURL, name, [])
#        #print name, util.getOutput(brw, [])
#        x.test_retval()
#
#def test_thread():
#    ths = []
#    for i in range(10):
#        x=Future(tt, 'thread'+str(i))
#        ths.append(x)
#    
#    for i in ths:
#        print i()
#
#def test_suite():
#    suite = unittest.TestSuite()
#    suite.addTest(unittest.makeSuite(liveserverTest))
#    #suite.addTest(unittest.makeSuite(liveserverBenchmark))
#    return suite
#
#if __name__ == '__main__':
#    evto = os.getenv('LIVESERVER_TIMEOUT')
#    if evto:
#        try:
#            TIMEOUT = int(evto)
#        except:
#            pass
#    
#    #unittest.main(defaultTest='test_suite')
#    
#    test_thread()




import asyncore
import socket, time
import StringIO
import mimetools, urlparse

class async_http(asyncore.dispatcher_with_send):
    # asynchronous http client

    def __init__(self, host, port, path, consumer, data=None):
        asyncore.dispatcher_with_send.__init__(self)

        self.host = host
        self.port = port
        self.path = path
        self.data = data

        self.consumer = consumer

        self.status = None
        self.header = None

        self.bytes_in = 0
        self.bytes_out = 0

        self.data = ""

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

    def handle_connect(self):
        # connection succeeded
        if self.data:
            wiredata = urllib.urlencode(data)
            
            text = "POST %s HTTP/1.0\r\n"+ \
                "Host: %s\r\n"+\
                "Content-Type: application/x-www-form-urlencoded\r\n"+\
                "Content-Length: %s\r\n"+\
                "\r\n%s" % (self.path, self.host, str(len(wiredata)), wiredata)
        else:
            text = "GET %s HTTP/1.0\r\nHost: %s\r\n\r\n" % (self.path, self.host)
        self.send(text)
        self.bytes_out = self.bytes_out + len(text)
        
        print text

    def handle_expt(self):
        # connection failed; notify consumer
        self.close()
        self.consumer.http_failed(self)

    def handle_read(self):

        data = self.recv(2048)
        self.bytes_in = self.bytes_in + len(data)

        if not self.header:
            # check if we've seen a full header

            self.data = self.data + data

            header = self.data.split("\r\n\r\n", 1)
            if len(header) <= 1:
                return
            header, data = header

            # parse header
            fp = StringIO.StringIO(header)
            self.status = fp.readline().split(" ", 2)
            self.header = mimetools.Message(fp)

            self.data = ""

            self.consumer.http_header(self)

            if not self.connected:
                return # channel was closed by consumer

        if data:
            self.consumer.feed(data)

    def handle_close(self):
        self.consumer.close()
        self.close()

def do_request(uri, consumer):

    # turn the uri into a valid request
    scheme, host, path, params, query, fragment = urlparse.urlparse(uri)
    assert scheme == "http", "only supports HTTP requests"
    try:
        host, port = host.split(":", 1)
        port = int(port)
    except (TypeError, ValueError):
        port = 80 # default port
    if not path:
        path = "/"
    if params:
        path = path + ";" + params
    if query:
        path = path + "?" + query

    return async_http(host, port, path, consumer)

class base_consumer:
    def __init__(self):
        self.data=''
    def http_header(self, client):
        self.host = client.host
        print self.host, repr(client.status)
    def http_failed(self, client):
        print self.host, "failed"
    def feed(self, data):
        print self.host, len(data)
        self.data+=data
    def close(self):
        print self.host, "CLOSE"

class in_consumer(base_consumer):
    def close(self):
        print self.host, "CLOSE"
        #megjott a html
        print self.data

class html_consumer(base_consumer):
    def close(self):
        print self.host, "CLOSE"
        #megjott a html
        
        uid = UID_EXTRACT.search(self.data,re.S)
        uid = uid.group(1)
        
        dc = in_consumer()
        wireurl = INURL % {'uuid':uid}
        do_request(wireurl, dc)


dc = html_consumer()
do_request(BASEURL, dc)

asyncore.loop()

#print dc.data