# -*- coding: utf-8 -*-

import grok
from megrok.menu import Menu
from grokui.base import IGrokUIRealm, GrokUILayer

grok.layer(GrokUILayer)
grok.context(IGrokUIRealm)


class Header(grok.ViewletManager):
    grok.name('grokui_header')


class Footer(grok.ViewletManager):
    grok.name('grokui_footer')


class Messages(grok.ViewletManager):
    grok.name('grokui_messages')


class MainMenu(Menu):
    grok.name('grokui_mainmenu')
    grok.title('Grok user interface panels')
