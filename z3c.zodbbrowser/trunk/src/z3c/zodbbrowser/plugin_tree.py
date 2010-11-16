# -*- coding: UTF-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 Zope Foundation and Contributors.
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
"""Plugin for object source display."""

import wx
from wax import *
from z3c.zodbbrowser.bases import BaseDisplayPlugin
twist_buttons = 1

from z3c.zodbbrowser.treehandler import rootHandler, baseHandler


class TreeDisplay(BaseDisplayPlugin):
    """MDIChildFrame - MDI parent"""

    #window title
    title = u"tree"

    def __init__(self, *arg, **kw):
        kw['direction'] = 'v'
        self.opener = kw.pop('opener')
        self.root = self.opener.getDataForDisplay('tree')

        super(TreeDisplay, self).__init__(*arg, **kw)

    def Body(self):
        """form layout setup
        tree on the left side
        one big textbox on the right side
        """
        self.SetTitle(self.title+" - "+self.opener.getTitle())

        splitter = Splitter(self, size=(500, 300))
        self.tree = TreeView(splitter, twist_buttons=twist_buttons, has_buttons=1)
        self.tree.OnItemExpanded = self.OnItemExpanded
        self.tree.OnSelectionChanged = self.OnTreeSelectionChanged
        self.tree.OnRightDown = self.OnItemRightClick

        self.textbox = TextBox(splitter, readonly=1, multiline=1)
        splitter.Split(self.tree, self.textbox, direction='v')
        self.AddComponent(splitter, expand='both')

        self.filltree()
        self.Pack()

        self.SetSize(self.GetParent().GetClientSizeTuple())

    def addItem(self, text, data, item=None):
        if item:
            child = self.tree.AppendItem(item, text)
        else:
            child = self.tree.AddRoot(text)

        data.loadedChild = False
        self.tree.SetPyData(child, data)
        if data.expandable:
            dummy = self.tree.AppendItem(child, "##expand##")

    def filltree(self):
        zz = rootHandler(self.root, 'root', self)
        self.addItem("root", zz)

    def OnItemExpanded(self, event):
        item = event.GetItem()
        if item:
            idata = self.tree.GetPyData(item)
            if isinstance(idata, baseHandler):
                if not idata.loadedChild:
                    idata.loadedChild = True
                    self.tree.DeleteChildren(item)
                    children = idata.getChildren()
                    for key, data in children:
                        self.addItem(key, data, item)
                idata.onExpanded()

    def OnTreeSelectionChanged(self, event):
        item = event.GetItem()
        if item:
            data = self.tree.GetPyData(item)
            if isinstance(data, baseHandler):
                data.onSelected()
            if data is None:
                data = self.tree.GetItemText(item)

    def OnItemRightClick(self, event):
        item, flags = self.tree.HitTest(event.GetPosition())
        if flags in [wx.TREE_HITTEST_ONITEMBUTTON, wx.TREE_HITTEST_ONITEMLABEL]:
            data = self.tree.GetPyData(item)
            if isinstance(data, baseHandler):
                self.tree.SelectItem(item)
                data.onRightClick()

    def setProps(self, data):
        u"""Write the data--information into the textbox"""
        self.textbox.SetValue(data['text'])

    def closeDB(self):
        self.opener.close()

    def OnClose(self, event):
        self.closeDB()
        event.Skip()


def register(registry):
    registry['db_display']['tree'] = TreeDisplay
