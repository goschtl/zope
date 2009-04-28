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
__docformat__ = "reStructuredText"

import ConfigParser
import logging
import mechanize
import os
import random
import sys
import time

from zc.testbrowser import browser, real, utils

FF2_USERAGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; '\
        'fr; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'

class BaseAnonymousBrowser:
    """A base class to implement powerful and anonymous browser from.
    This abstract classr may be used to write browsers that support proxies
    balancing

    """
    def __init__(self,
                 url = None,
                 config = None,
                 proxies = None,
                 user_agent = None,
                 proxy_max_use = None,
                 mech_browser = None,
                 *args, **kwargs):
        self._enable_setattr_errors = False
        if not proxies:
            proxies = []
        if not getattr(self, 'log', None):
            self.log = logging.getLogger(__name__)
        self.load_config(config)
        proxieslist = self.config.get('proxies', '').strip()
        self.proxies = [proxy.strip()
                        for proxy in proxieslist.split('\n')
                        if proxy.strip()]
        self.proxies.extend([p
                           for p in proxies
                           if not p in self.proxies])
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = self.config.get('user-agent',
                                               FF2_USERAGENT)
        # only enter proxified mode when we got a list of valid proxies
        self.proxified = False
        if self.proxies:
            self.proxified = True

        # intialize proxy balancing
        self._lastproxy = {'proxy':-1,
                           'count':0}
        # initiate proxy max use
        self.proxy_max_use = proxy_max_use

    def load_config(self, config):
        if not getattr(self, 'config', None):
            self.config = utils.get_ztb_config(config)

    def chooseProxy(self):
        choice = 0
        if len(self.proxies) < 2:
            # for 0 or 1 proxy, just get it
            choice = random.randint(0, len(self.proxies)-1)
        else:
            # for 2+ proxies in the list, we iterate to get a different proxy
            # for the last one used, if this one was too many used.
            # We also put a coin of the reuse of the proxy, we just dont go too
            # random
            proxy_not_chosen, maxloop = True, 200
            while proxy_not_chosen:
                # pile or face ! We reuse the proxy or not!
                if not self.proxy_max_use \
                   or (self._lastproxy['count'] >= 1) \
                   and (self._lastproxy['count'] < self.proxy_max_use):
                    # we do not always change proxy
                    if (self._lastproxy['proxy'] != -1) and random.randint(0, 1):
                        choice = self._lastproxy['proxy']
                    else:
                        choice = random.randint(0, len(self.proxies)-1)
                if self._lastproxy['proxy'] == choice:
                    if not self.proxy_max_use or (self._lastproxy['count'] <= self.proxy_max_use):
                        self._lastproxy['proxy'] = choice
                        proxy_not_chosen = False
                else:
                    self._lastproxy['proxy'] = choice
                    # reinitialize the proxy count
                    self._lastproxy['count'] = 0
                    proxy_not_chosen = False
                maxloop -= 1
                if not maxloop:
                    self.log.debug("Ho, seems we got the max wills "
                                   "to choose, something has gone wrong")
                    proxy_not_chosen = False
        self._lastproxy['count'] += 1
        return self.proxies[choice]

    def reset(self, url, data):
        """Reset the underlying browser to its initial state.
        (eg, just after init)
        Implementation example::

            try:
                self.browser_open('about:blank')
            except Exception, e:
                if not ('unknown url type:' in '%s' % e):
                    raise e
        """
        raise Exception('not implemented')

    def open(self, url, data=None, retrys=4, *args, **kwargs):
        """Wrapper to the underlyng browser class.
        It will do the neccessary things to proxisy the
        browser before hitting any url.
        @param url the url to hit
        @param retrys number of retrys allowed before crashing.
        """
        try:
            if self.proxified:
                self.proxify()
            if self.user_agent:
                self.fake_user_agent()
            return self.browser_open(url, data)
        except Exception, e:
            if retrys:
                # go to open blank to reset entirely all post and other stuff
                self.reset(url, data)

                # removing dead proxies
                if self.proxified:
                    if len(self.proxies) >= 1:
                        del self.proxies[self._lastproxy['proxy']]
                        self._lastproxy['proxy'] = -1
                        self._lastproxy['count'] = 0
                    else:
                        raise Exception("There are no valid proxies left")

                self.log.error('Retrying "%s", (left: %s)' % (url, retrys))
                retrys -= 1
                self.open(url, data, retrys)
            else:
                raise e

    def proxify(self, force=False):
        """Method to choose and set a proxy."""
        raise Exception('not implemented')

    def fake_user_agent(self, force=False):
        """Method to set the user agent."""
        raise Exception('not implemented')

    def browser_open(self, url, data=None):
        """Real method to hit the browser.
        Implementation example ::

            browser.Browser.open(self, url, data)

        """
        raise Exception('not implemented')

class AnonymousBrowser(BaseAnonymousBrowser, browser.Browser):
    """A proxified mechanize based browser."""

    def __init__(self,
                 url=None,
                 config=None,
                 mech_browser=None,
                 proxies = [],
                 user_agent=None,
                 proxy_max_use=None,
                 *args, **kwargs):
        BaseAnonymousBrowser.__init__(self,
                                      url = url,
                                      config = config,
                                      proxies = proxies,
                                      user_agent=user_agent,
                                      proxy_max_use=proxy_max_use,
                                      *args, **kwargs)
        self._enable_setattr_errors = False
        self.test=kwargs.get('test',False)
        if mech_browser is None:
            mech_browser = mechanize.Browser()
        self.mech_browser = mech_browser
        if url is not None:
            BaseAnonymousBrowser.open(self, url)

    def reset(self, url, data):
        pass

    def fake_user_agent(self, force=False):
        self.mech_browser.set_handle_robots(False)
        self.mech_browser.addheaders = [('User-agent' , self.user_agent)]

    def browser_open(self, url, data=None):
        self.timer = browser.PystoneTimer()
        self.raiseHttpErrors = True
        return browser.Browser.open(self, url, data)

    def proxify(self, force=False):
        """"""
        if (self.proxified or force) and self.proxies:
            proxy = self.chooseProxy()
            self.mech_browser.set_proxies(
                {'http': proxy,
                 'https': proxy}
            )

class FirefoxBrowser(BaseAnonymousBrowser, real.Browser):
    """A proxified mechanize based browser."""

    def __init__(self,
                 url=None,
                 host = None,
                 port=None,
                 firefox_binary = None,
                 profile_klass = None,
                 config=None,
                 proxies = [],
                 user_agent=None,
                 proxy_max_use=None,
                 *args, **kwargs):
        BaseAnonymousBrowser.__init__(self,
                                      url = url,
                                      config = config,
                                      proxies = proxies,
                                      user_agent=user_agent,
                                      proxy_max_use=proxy_max_use,
                                      *args, **kwargs)
        preferences= {}
        if self.user_agent:
            preferences["general.useragent.override"] =  self.user_agent
        real.Browser. __init__(self,
                               url=None,
                               host = host,
                               port=port,
                               firefox_binary = firefox_binary,
                               profile_klass = profile_klass,
                               config=config,
                               preferences = preferences,
                               *args, **kwargs)

        if url is not None:
            BaseAnonymousBrowser.open(self, url)

    def browser_open(self, url, data=None):
        return real.Browser.open(self, url, data)

    def fake_user_agent(self, force=False):
        """Done in __init__, you cannont change it without restarting firefox"""
        if force:
            user_agent_prefs = {"general.useragent.override": self.user_agent}
            self.update_profile(user_agent_prefs)
            self.restart_ff()

    def reset(self, url, data):
        self.restart_ff()
        self.open(url, data)

    def browser_open(self, url, data=None):
        return real.Browser.open(self, url, data)

    def proxify(self, force=False):
        """"""
        if (self.proxified or force) and self.proxies:
            host, port = self.chooseProxy().split(':')
            proxy_prefs = {
                'network.proxy.http':   host,
                'network.proxy.ftp':    host,
                'network.proxy.gopher': host,
                'network.proxy.socks':  host,
                'network.proxy.ssl':    host,
                'network.proxy.http_port':   port,
                'network.proxy.ftp_port':    port,
                'network.proxy.gopher_port': port,
                'network.proxy.socks_port':  port,
                'network.proxy.ssl_port':    port,
                'network.proxy.type': 1,
                'network.proxy.no_proxy_on': '',
            }
            self.update_profile(proxy_prefs)



