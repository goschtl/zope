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
"""

Revision information: $Id: contents.py,v 1.21 2003/06/12 09:30:48 jim Exp $
"""

from zope.app import zapi
from zope.app.interfaces.container import IContainer, IZopeContainer
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.size import ISized
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView
from zope.app.interfaces.copypastemove import IPrincipalClipboard
from zope.app.interfaces.copypastemove import IObjectCopier
from zope.app.interfaces.copypastemove import IObjectMover
from zope.app.interfaces.container import IPasteTarget
from zope.app.interfaces.container import ICopySource, IMoveSource
from zope.app.interfaces.dublincore import IDCDescriptiveProperties
from zope.app.i18n import ZopeMessageIDFactory as _

from zope.app.browser.container.adding import BasicAdding


class Contents(BrowserView):

    __used_for__ = IContainer

    error = ''
    message = ''
    normalButtons = False
    specialButtons = False

    def listContentInfo(self):
        request = self.request

        if  "container_cancel_button" in request:
            if "type_name" in request:
                del request.form['type_name']
            if "rename_ids" in request and "new_value" in request:
                del request.form['rename_ids']
            if "retitle_id" in request and "new_value" in request:
                del request.form['retitle_id']

            return self._normalListContentsInfo()

        elif "type_name" in request and "new_value" in request:
            self.addObject()
        elif "rename_ids" in request and "new_value" in request:
            self.renameObjects()
        elif "retitle_id" in request and "new_value" in request:
            self.changeTitle()
        elif "container_cut_button" in request:
            self.cutObjects()
        elif "container_copy_button" in request:
            self.copyObjects()
        elif "container_paste_button" in request:
            self.pasteObjects()
        elif "container_delete_button" in request:
            self.removeObjects()
        else:
            return self._normalListContentsInfo()

        if self.error:
            return self._normalListContentsInfo()

        status = request.response.getStatus()
        if status not in (302, 303):
            # Only redirect if nothing else has
            request.response.redirect(request.URL)
        return ()

    def _normalListContentsInfo(self):
        request = self.request

        self.specialButtons = (
                 'type_name' in request or
                 'rename_ids' in request or
                 'container_rename_button' in request or
                 'retitle_id' in request
                 )
        self.normalButtons = not self.specialButtons

        info = map(self._extractContentInfo,
                   zapi.getAdapter(self.context, IZopeContainer).items())

        self.supportsCut = (
            info and zapi.queryAdapter(self.context, IMoveSource) is not None)
        self.supportsCopy = (
            info and zapi.queryAdapter(self.context, ICopySource) is not None)
        self.supportsPaste = (
            zapi.queryAdapter(self.context, IPasteTarget) is not None)

        self.supportsRename = self.supportsCut and self.supportsPaste

        return info
        

    def _extractContentInfo(self, item):
        request = self.request


        rename_ids = {}
        if "container_rename_button" in request:
            for rename_id in request.get('ids', ()):
                rename_ids[rename_id] = rename_id
        elif "rename_ids" in request:
            for rename_id in request.get('rename_ids', ()):
                rename_ids[rename_id] = rename_id
                
        
        retitle_id = request.get('retitle_id')
        
        id, obj = item
        info = {}
        info['id'] = info['cb_id'] = id
        info['object'] = obj

        info['url'] = id
        info['rename'] = rename_ids.get(id)
        info['retitle'] = id == retitle_id
        

        zmi_icon = zapi.queryView(obj, 'zmi_icon', self.request)
        if zmi_icon is None:
            info['icon'] = None
        else:
            info['icon'] = zmi_icon()

        dc = zapi.queryAdapter(obj, IZopeDublinCore)
        if dc is not None:
            info['retitleable'] = id != retitle_id
            info['plaintitle'] = 0
            
            title = dc.title
            if title:
                info['title'] = title

            formatter = self.request.locale.getDateTimeFormatter('short')
            created = dc.created
            if created is not None:
                info['created'] = formatter.format(created)

            modified = dc.modified
            if modified is not None:
                info['modified'] = formatter.format(modified)
        else:
            info['retitleable'] = 0
            info['plaintitle'] = 1


        sized_adapter = zapi.queryAdapter(obj, ISized)
        if sized_adapter is not None:
            info['size'] = sized_adapter
        return info

    def renameObjects(self):
        """Given a sequence of tuples of old, new ids we rename"""
        request = self.request
        ids = request.get("rename_ids")
        newids = request.get("new_value")

        for id, newid in map(None, ids, newids):
            if newid != id:
                container = zapi.getAdapter(self.context, IZopeContainer)
                container.rename(id, newid)

    def changeTitle(self):
        """Given a sequence of tuples of old, new ids we rename"""
        request = self.request
        id = request.get("retitle_id")
        new = request.get("new_value")

        item = self.context[id]
        dc = zapi.getAdapter(item, IDCDescriptiveProperties)
        dc.title = new

    def addObject(self):
        request = self.request
        new = request["new_value"]
        if new:
            adding = zapi.queryView(self.context, "+", request)
            if adding is None:
                adding = BasicAdding(self.context, request)
            else:
                # Set up context so that the adding can build a url
                # if the type name names a view.
                # Note that we can't so this for the "adding is None" case
                # above, because there is no "+" view.
                adding = zapi.ContextWrapper(adding, self.context, name="+")

            adding.action(request['type_name'], new)

            

            
    def removeObjects(self):
        """Remove objects specified in a list of object ids"""
        request = self.request
        ids = request.get('ids')
        if not ids:
            self.error = _("You didn't specify any ids to rename.")
            return
                 
        container = zapi.getAdapter(self.context, IZopeContainer)
        for id in ids:
            container.__delitem__(id)

    def copyObjects(self):
        """Copy objects specified in a list of object ids"""
        request = self.request
        ids = request.get('ids')
        if not ids:
            self.error = _("You didn't specify any ids to copy.")
            return
                 
        container_path = zapi.getPath(self.context)

        user = self.request.user
        annotationsvc = zapi.getService(self.context, 'PrincipalAnnotation')
        annotations = annotationsvc.getAnnotations(user)
        clipboard = zapi.getAdapter(annotations, IPrincipalClipboard)
        clipboard.clearContents()
        items = []
        for id in ids:
            items.append(zapi.joinPath(container_path, id))
        clipboard.addItems('copy', items)

    def cutObjects(self):
        """move objects specified in a list of object ids"""
        request = self.request
        ids = request.get('ids')
        if not ids:
            self.error = _("You didn't specify any ids to cut.")
            return

        container_path = zapi.getPath(self.context)

        user = self.request.user
        annotationsvc = zapi.getService(self.context, 'PrincipalAnnotation')
        annotations = annotationsvc.getAnnotations(user)
        clipboard = zapi.getAdapter(annotations, IPrincipalClipboard)
        clipboard.clearContents()
        items = []
        for id in ids:
            items.append(zapi.joinPath(container_path, id))
        clipboard.addItems('cut', items)

    def pasteObjects(self):
        """Iterate over clipboard contents and perform the
           move/copy operations"""
        target = self.context

        user = self.request.user
        annotationsvc = zapi.getService(self.context, 'PrincipalAnnotation')
        annotations = annotationsvc.getAnnotations(user)
        clipboard = zapi.getAdapter(annotations, IPrincipalClipboard)
        items = clipboard.getContents()
        for item in items:
            obj = zapi.traverse(target, item['target'])
            if item['action'] == 'cut':
                zapi.getAdapter(obj, IObjectMover).moveTo(target)
                clipboard.clearContents()
            elif item['action'] == 'copy':
                zapi.getAdapter(obj, IObjectCopier).copyTo(target)
            else:
                raise

    def hasClipboardContents(self):
        """ interogates the PrinicipalAnnotation to see if
           clipboard contents exist """

        if not self.supportsPaste:
            return False

        user = self.request.user

        annotationsvc = zapi.getService(self.context, 'PrincipalAnnotation')
        annotations = annotationsvc.getAnnotations(user)
        
        clipboard = zapi.getAdapter(annotations, IPrincipalClipboard)

        if clipboard.getContents():
            return True

        return False

    contents = ViewPageTemplateFile('contents.pt')
    contentsMacros = contents

    _index = ViewPageTemplateFile('index.pt')

    def index(self):
        if 'index.html' in self.context:
            self.request.response.redirect('index.html')
            return ''

        return self._index()

class JustContents(Contents):
    """Like Contents, but does't delegate to item named index.html
    """

    def index(self):
        return self._index()
