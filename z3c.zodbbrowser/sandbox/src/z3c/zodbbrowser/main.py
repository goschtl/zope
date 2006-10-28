# -*- coding: UTF-8 -*-

import os
import sys
import glob
import wx

try:
    from wax import *
    from wax.tools.choicedialog import ChoiceDialog
except ImportError:
    print "You do not have `wax` installed, please download it from http://sourceforge.net/projects/waxgui"

twist_buttons=1

from z3c.zodbbrowser import __title__
from z3c.zodbbrowser.utils import *
from z3c.zodbbrowser.registry import getSourcePlugins
from z3c.zodbbrowser.registry import getDBDisplayPlugins
from z3c.zodbbrowser.registry import installplugins
from z3c.zodbbrowser.treehandler import rootHandler, baseHandler

class ZODBFrame(MDIParentFrame):
    
    #def __init__(self):
    #    super(ZODBFrame, self).__init__(size=(640,480))
    #    self.SetSize((800, 600))
    
    def Body(self):
        self.SetTitle(__title__)
        
        if WAX_VERSION_TUPLE < (0,3,33):
            ShowMessage(__title__,
                        "WARNING: wax version 0.3.33 required!")
        
        self.CreateStatusBar()
        self.SetStatusText("This is the statusbar")
        
        menubar = MenuBar(self)

        menu1 = Menu(self)
        
        opts = getSourcePlugins()
        for title, ext, klass in opts:
            menu1.Append("Open %s" % title,
                         curry(self.menuOpen, klass),
                         "This the text in the statusbar")
            
        menu1.Append("&Open\tCTRL+O", self.menuOpen, 
            "This the text in the statusbar")
        menu1.Append("&Close", self.menuClose)
        menu1.AppendSeparator()
        menu1.Append("E&xit\tALT+X", self.menuExit, "Exit")
        
        menubar.Append(menu1, "&File")
        
        self.SetMenuBar(menubar)
        
        #self.Pack()
        
        #self.SetSize((800, 600))
        #self.CenterOnScreen()
    
    def menuOpen(self, openerklass, event=None):
        opener = openerklass(self)
        if opener.open(self):
            viewopts = opener.getSupportedDisplays()
            
            frameklasses = getDBDisplayPlugins(viewopts)
            
            klassindex = None
            if len(frameklasses) == 0:
                ShowMessage(__title__,
                    "Happens that there is no display plugin for %s" % \
                    viewopts)
            elif len(frameklasses) == 1:
                klassindex = 0
            else:
                opts = [ii.title for ii in frameklasses]
                dlg = ChoiceDialog(self,
                                   title=__title__,
                                   prompt="Choose an display method",
                                   choices=opts)
                try:
                    result = dlg.ShowModal()
                    if result == 'ok':
                        klassindex = dlg.choice
                finally:
                    dlg.Destroy()
            
            if klassindex is not None:
                frame = frameklasses[klassindex](parent=self,
                                                 opener = opener)
                frame.Show()
    
    def menuClose(self, event):
        #self.Close()
        while True:
            chld = self.GetActiveChild()
            if chld:
                print 'close1'
                chld.Close()
            else:
                break
        pass
    
    def menuExit(self, event):
        self.Destroy()

class MyApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        frame = ZODBFrame()
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def main():
    installplugins()
    
    app = Application(ZODBFrame)
    #app = MyApp(False)
    app.MainLoop()

if __name__ == '__main__':
    main()
