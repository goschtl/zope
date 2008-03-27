// Add a comment action that ignores its arguments
Selenium.prototype.doComment = function(text, text) {
};


Selenium.prototype.doDeleteCookie = function(name,path) {
    /**
     * Delete a named cookie with specified path.
     *
     * @param name the name of the cookie to be deleted
     * @param path the path property of the cookie to be deleted
     *
     * Backport from Selenium 0.8.2
     */
    // set the expire time of the cookie to be deleted to one minute before now.
    path = path.trim();
    if (browserVersion.khtml) {
        // Safari and conquerer don't like paths with / at the end
        if ("/" != path) {
            path = path.replace(/\/$/, "");
        }
    }
    var expireDateInMilliseconds = (new Date()).getTime() + (-1 * 1000);
    var cookie = name.trim() + "=deleted; path=" + path + "; expires=" + new Date(expireDateInMilliseconds).toGMTString();
    LOG.debug("Setting cookie to: " + cookie);
	return this.page().currentDocument.cookie = cookie;
}
