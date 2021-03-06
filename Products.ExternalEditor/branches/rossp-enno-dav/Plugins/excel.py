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
"""External Editor MSExcel Plugin

$Id$
"""

import os
from time import sleep
import win32com
from win32com import client # Initialize Client module

class EditorProcess:
    def __init__(self, file):
        """Launch editor process"""
        excel = win32com.client.Dispatch('Excel.Application')
        # Try to open the file, keep retrying until we succeed or timeout
        i = 0
        timeout = 45
        while i < timeout:
            try:
                excel.Workbooks.Open(file)
            except:
                i += 1
                if i >= timeout:
                    raise RuntimeError('Could not launch Excel.')
                sleep(1)
            else:
                break
        excel.Visible = 1
        self.excelapp = excel
        self.file = file
        
    def wait(self, timeout):
        """Wait for editor to exit or until timeout"""
        sleep(timeout)
            
    def isAlive(self):
        """Returns true if the editor process is still alive"""
        head, tail = os.path.split(self.file)
        head, tail = head.lower(), tail.lower()
        for doc in self.excelapp.Workbooks:
            if head == doc.Path.lower() and tail == doc.Name.lower():
                return 1
        return 0

def test():
    import os
    from time import sleep
    from tempfile import mktemp
    fn = mktemp('.html')
    f = open(fn, 'w')
    f.write('<html>\n  <head></head>\n<body>\n'
            '<table><tr><th>Column 1</th><th>Column 2</th></tr>' 
            '<tr><td>1234</td><td>3689</td></tr>'
            '<tr><td>2345</td><td>3789</td></tr>'
            '<tr><td>3456</td><td>3889</td></tr>'
            '</body>\n</html>')
    f.close()
    print 'Connecting to Excel...'
    f = EditorProcess(fn)
    print 'Attached to %s %s' % (`f.excelapp`, f.excelapp.Version)
    print ('%s is open...' % fn),
    if f.isAlive():
        print 'yes'
        print 'Test Passed.'
    else:
        print 'no'
        print 'Test Failed.'
    
if __name__ == '__main__':
    test()
