##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
import zope.deprecation

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from z3c.optionstorage.interfaces import IOptionStorage
from z3c.optionstorage import OptionDict

def checkFields(request, *fields):
    for field in fields:
        if field not in request:
            return False
    return True

class StorageNameNotFoundError(LookupError):
    pass

class OptionStorageView(object):

    storagetemplate = ViewPageTemplateFile("optionstorage.pt")
    dicttemplate = ViewPageTemplateFile("optiondict.pt")

    dictlist = [] # (name, topic)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.name = None
        self.topic = None
        self.dict = None

    def getNameTopicList(self):
        storage = IOptionStorage(self.context)
        for name, topic in self.dictlist:
            yield {"name": name, "topic": topic}

    def __call__(self, name=None):
        if name is None:
            return self.storagetemplate()

        storage = IOptionStorage(self.context)
        for _name, topic in self.dictlist:
            if name == _name:
                if name not in storage:
                    storage[name] = OptionDict()
                self.dict = storage[name]
                self.name = name
                self.topic = topic
                break
        else:
            raise StorageNameNotFoundError

        form = self.request.form
        if "SAVE" not in form:
            return self.dicttemplate()

        language = {}
        key = {}
        value = {}
        for entry in form:
            entryvalue = form[entry].strip()
            if not entryvalue:
                pass
            elif entry.startswith("lang-"):
                language[int(entry[5:])] = entryvalue
            elif entry.startswith("key-"):
                key[int(entry[4:])] = entryvalue
            elif entry.startswith("value-"):
                tok = entry.split("-")
                value[int(tok[1]), int(tok[2])] = entryvalue

        try:
            defaultkey = int(form["default-key"])
        except KeyError:
            defaultkey = None

        try:
            defaultlanguage = int(form["default-lang"])
        except KeyError:
            defaultlanguage = None

        self.dict.delAllValues()
        for keynum, languagenum in value:
            if keynum in key and languagenum in language:
                self.dict.addValue(key[keynum], language[languagenum],
                                   value[keynum, languagenum])
        if defaultkey in key:
            self.dict.setDefaultKey(key[defaultkey])
        if defaultlanguage in language:
            self.dict.setDefaultLanguage(language[defaultlanguage])

        return self.dicttemplate()

