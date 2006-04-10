# -*- coding: UTF-8 -*-

import os
import sys
import time
import urllib2
import subprocess
from base64 import encodestring

from zope.testbrowser.browser import Browser

started_byus = False
popen_handle = None

USER = "globalmgr"
PWD = "globalmgrpw"

ROOTURL = ''
SRVCONTROLURL = '/++etc++process/servercontrol.html'

def getAuth(usr, pwd):
    auth = "Basic %s" % encodestring("%s:%s" % (usr, pwd)
                                 ).replace("\012", "")
    return auth

def check_server(url):
    brw = Browser()
    try:
        brw.open(url)
        return True
    except urllib2.HTTPError, e:
        return False
    except IOError, e:
        return False

def stop_zope(force=False):
    global started_byus
    global ROOTURL
    
    if started_byus or force:
        print "Stopping Z3 server"
        
        brw = Browser()
        brw.addHeader('Authorization', getAuth(USER, PWD))
        brw.open(ROOTURL+SRVCONTROLURL)
        brw.getControl(name="shutdown").click()
        
        print "Stopped"

def start_zope(rooturl, env=None, force=False):
    global started_byus
    global popen_handle
    global ROOTURL
    ROOTURL = rooturl
    
    started_byus = not check_server(rooturl)
    
    if started_byus or force:
        print "Starting Z3 server now:"
        
        try:
            import zope
        except ImportError:
            print "Please put the zope3/src in your pythonpath"
            
        here = os.path.abspath(os.path.dirname(sys.argv[0]))
        zskel = os.path.join(here, "zopeskel")
        
        #no better idea at the time
        runzope = "python "+os.path.join(zskel, "runzope.py")
        #os.system(runzope)
        #os.startfile(runzope)
        #os.spawnl(os.P_NOWAIT, runzope)
        popen_handle = subprocess.Popen(runzope, shell=True, env=env)
        
        while not check_server(rooturl):
            print ".",
            time.sleep(1)
        
        print
        print "server started"
        
        sys.exitfunc = stop_zope
    else:
        print "Z3 server already running, make sure that parameters, users match!"

if __name__ == '__main__':
    start_zope()