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


/********************************************************************
 * The following code is a selenium plugin taken from
 * http://wiki.openqa.org/display/SEL/waitForCondition which can be
 * used to wait for a given javascript condition to be true.  This
 * is useful for AJAX testing.  See
 * http://agiletesting.blogspot.com/2006/03/ajax-testing-with-selenium-using_21.html
 * for more information.  The code is Copyright ThoughtWorks, Inc. 2006
 * and is licensed under the Apache license 2.0:
 * http://www.apache.org/licenses/LICENSE-2.0
 **********************************************************************/
// Waits for the condition to be "true"
Selenium.prototype.doWaitForCondition = function(script, timeout) {
  if (isNaN(timeout)) {
    throw new SeleniumError("Timeout is not a number: " + timeout);
  }

  TestLoop.waitForCondition = function () {
    return eval(script);
  };

  TestLoop.waitForConditionStart = new Date().getTime();
  TestLoop.waitForConditionTimeout = timeout;

  TestLoop.pollUntilConditionIsTrue = function () {
    try {
      if (this.waitForCondition()) {
        this.waitForCondition = null;
        this.waitForConditionStart = null;
        this.waitForConditionTimeout = null;
        this.continueCommandExecutionWithDelay();
      } else {
        if (this.waitForConditionTimeout != null) {
          var now = new Date();
          if ((now - this.waitForConditionStart) > this.waitForConditionTimeout) {
            throw new SeleniumError("Timed out after " + this.waitForConditionTimeout + "ms");
          }
        }
        window.setTimeout("TestLoop.pollUntilConditionIsTrue()", 10);
      }
    } catch (e) {
      var lastResult = new CommandResult();
      lastResult.failed = true;
      lastResult.failureMessage = e.message;
      this.commandComplete(lastResult);
      this.testComplete();
    }
  };
};
