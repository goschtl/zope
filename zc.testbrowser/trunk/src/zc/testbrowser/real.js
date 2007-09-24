var tb_tokens = {};
var tb_next_token = 0;

tb_page_loaded = false;
document.getElementById("appcontent"
    ).addEventListener("load", function() { tb_page_loaded = true; }, true);

function tb_xpath(pattern, context) {
    if (context == null)
        context = content.document;
    return content.document.evaluate(
        pattern, context, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
}

function tb_get_link_by_predicate(predicate, index) {
    var anchors = content.document.getElementsByTagName('a');
    var i=0;
    var found = null;
    if (index == undefined) index = null;
    for (var x=0; x < anchors.length; x++) {
        a = anchors[x];
        if (!predicate(a)) {
            continue;
        }
        // this anchor matches

        // if we weren't given an index, but we found more than
        // one match, we have an ambiguity
        if (index == null && i > 0) {
            return 'ambiguity error';
        }

        found = x;

        // if we were given an index and we just found it, stop
        if (index != null && i == index) {
            break
        }
        i++;
    }
    if (found != null) {
        tb_tokens[tb_next_token] = anchors[found];
        return tb_next_token++;
    }
    return false; // link not found
}

function tb_normalize_whitespace(text) {
    text = text.replace(/[\n\r]+/g, ' ');
    text = text.replace(/\s+/g, ' ');
    text = text.replace(/ +$/g, '');
    text = text.replace(/^ +/g, '');
    return text;
}

function tb_get_link_by_text(text, index) {
    text = tb_normalize_whitespace(text);
    return tb_get_link_by_predicate(
        function (a) {
            return tb_normalize_whitespace(a.textContent).indexOf(text) != -1;
        }, index)
}

function tb_get_link_by_url(url, index) {
    return tb_get_link_by_predicate(
        function (a) {
            return a.href.indexOf(url) != -1;
        }, index)
}

function tb_get_link_by_id(id, index) {
    var found = content.document.getElementById(id);
    if (found != null) {
        tb_tokens[tb_next_token] = found;
        return tb_next_token++;
    }
    return false; // link not found
}

function tb_take_screen_shot(out_path) {
    // The `subject` is what we want to take a screen shot of.
    var subject = content.document;
    var canvas = content.document.createElement('canvas');
    canvas.width = subject.width;
    canvas.height = subject.height;

    var ctx = canvas.getContext('2d');
    ctx.drawWindow(content, 0, 0, subject.width, subject.height, 'rgb(0,0,0)');
    tb_save_canvas(canvas, out_path);
}

function tb_save_canvas(canvas, out_path) {
    var io = Components.classes['@mozilla.org/network/io-service;1'
        ].getService(Components.interfaces.nsIIOService);
    var source = io.newURI(canvas.toDataURL('image/png', ''), 'UTF8', null);
    var persist = Components.classes[
        '@mozilla.org/embedding/browser/nsWebBrowserPersist;1'
        ].createInstance(Components.interfaces.nsIWebBrowserPersist);
    var file = Components.classes['@mozilla.org/file/local;1'
        ].createInstance(Components.interfaces.nsILocalFile);
    file.initWithPath(out_path);
    persist.saveURI(source, null, null, null, null, file);
}

function tb_follow_link(token) {
    var a = tb_tokens[token];
    var evt = a.ownerDocument.createEvent('MouseEvents');
    evt.initMouseEvent('click', true, true, a.ownerDocument.defaultView,
        1, 0, 0, 0, 0, false, false, false, false, 0, null);
    a.dispatchEvent(evt);
    // empty the tokens data structure, they're all expired now
    tb_tokens = {};
}

function tb_get_link_text(token) {
    return tb_normalize_whitespace(tb_tokens[token].textContent);
}

function tb_get_control_by_predicate(
    predicate, index, allowDuplicate, context, xpath) {
    if (xpath == null) {
        var xpath = '//input | //select | //option | //textarea';
    }
    var res = tb_xpath(xpath, context)
    var i=0;
    var found = null;
    if (index == undefined) index = null;
    for (var x = 0; x < res.snapshotLength; x++) {
        elem = res.snapshotItem(x);
        if (!predicate(elem)) {
            continue;
        }
        // if we weren't given an index, but we found more than
        // one match, we have an ambiguity
        if (index == null && i > 0) {
            return 'ambiguity error';
        }
        found = elem;

        // if we were given an index and we just found it, stop
        if (index != null && i == index) {
            break;
        }

        // One exception is when the name of a radio or checkbox input is
        // found twice
        if (allowDuplicate) {
            inputType = elem.getAttribute('type');
            if (inputType == 'radio' || inputType == 'checkbox') {
                break;
            }
        }
        i++;
    }
    if (found != null) {
        tb_tokens[tb_next_token] = found;
        return tb_next_token++;
    }
    return false; // control not found
}


function tb_get_control_by_label(text, index, contextToken, xpath) {
    context = null;
    if (contextToken != null) {
        context = tb_tokens[contextToken];
    }
    text = tb_normalize_whitespace(text);
    return tb_get_control_by_predicate(
        function (control) {
            var tag = control.tagName;
            var labelText = null;
            if (tag == 'OPTION') {
                labelText = control.textContent;
                if (control.hasAttribute('label')) {
                    labelText += ' ' + control.getAttribute('label');
                }
            }
            else if (tag == 'SUBMIT' || tag == 'BUTTON') {
                labelText = control.getAttribute('value');
            }
            else {
                var id = control.getAttribute('id');
                var name = control.getAttribute('name');
                // The label element references the control id
                var res = tb_xpath("//label[@for='" + id + "']")
                // The label encloses the input element
                if (res.snapshotLength == 0) {
                    var res = tb_xpath("ancestor::label", control);
                }
                // Collect all text content, since HTML allows multiple labels
                // for the same input.
                if (res.snapshotLength > 0) {
                    labelText = '';
                    for (var c = 0; c < res.snapshotLength; c++) {
                        labelText += ' ' + tb_normalize_whitespace(
                            res.snapshotItem(c).textContent);
                    }
                }
            }
            // We can only match whole words! Sigh!
            if (labelText == null)
                return false;
            var expr = ('(^| )\\W*' +
                        text.replace(/(\W)/gi, '\\$1') +
                        '\\W*($| [^a-zA-Z]*)');
            if (labelText.search(expr) == -1)
                return false;
            return true;
        }, index, false, context, xpath)
}

function tb_get_control_by_name(name, index) {
    return tb_get_control_by_predicate(
        function (control) {
            var controlName = control.getAttribute('name');
            return controlName != null && controlName.indexOf(name) != -1;
        }, index, true)
}

function tb_get_listcontrol_options(token) {
    var elem = tb_tokens[token];
    var tagName = elem.tagName;
    var options = new Array();
    if (tagName == 'SELECT') {
        var res = tb_xpath('child::option', elem)
        for (var c = 0; c < res.snapshotLength; c++) {
            options.push(res.snapshotItem(c).getAttribute('value'));
        }
    }
    return options.toSource();
}

function tb_get_listcontrol_displayOptions(token) {
    var elem = tb_tokens[token];
    var tagName = elem.tagName;
    var options = new Array();
    if (tagName == 'SELECT') {
        var res = tb_xpath('child::option', elem)
        for (var c = 0; c < res.snapshotLength; c++) {
            item = res.snapshotItem(c)
            if (item.hasAttribute('label'))
                options.push(item.getAttribute('label'))
            else
                options.push(item.textContent);
        }
    }
    return options.toSource();
}

function tb_get_listcontrol_value(token) {
    var elem = tb_tokens[token];
    var tagName = elem.tagName;
    var values = new Array();
    if (tagName == 'SELECT') {
        var res = tb_xpath('child::option', elem)
        for (var c = 0; c < res.snapshotLength; c++) {
            var item = res.snapshotItem(c);
            if (item.selected)
                values.push(res.snapshotItem(c).getAttribute('value'));
        }
    } else if (tagName == 'INPUT') {
        var elemName = elem.getAttribute('name');
        var res = tb_xpath('//input[@name="' +
                           elemName +
                           '"][@type="radio"]', elem);
        for (var c = 0; c < res.snapshotLength; c++) {
            var item = res.snapshotItem(c);
            if (item.checked) {
                values.push(item.getAttribute('value'));
            }
        }
    }
    return values.toSource();
}

function tb_get_listcontrol_displayValue(token) {
    var elem = tb_tokens[token];
    var tagName = elem.tagName;
    var options = new Array();
    if (tagName == 'SELECT') {
        var res = tb_xpath('child::option', elem)
        for (var c = 0; c < res.snapshotLength; c++) {
            var item = res.snapshotItem(c);
            if (item.selected)
                options.push(item.textContent);
        }
    }
    return options.toSource();
}

function tb_set_listcontrol_displayValue(token, value) {
    var elem = tb_tokens[token];
    var tagName = elem.tagName;
    var options = new Array();
    if (tagName == 'SELECT') {
        var res = tb_xpath('child::option', elem)
        for (var c = 0; c < res.snapshotLength; c++) {
            var item = res.snapshotItem(c);
            if (value.indexOf(item.textContent) != -1)
                item.selected = true;
            else
                item.selected = false;
        }
    }
    return options.toSource();
}

function tb_get_listcontrol_item_tokens(token) {
    var elem = tb_tokens[token];
    var tagName = elem.tagName;
    var tokens = new Array();
    if (tagName == 'SELECT') {
        var res = tb_xpath('child::option', elem);
        for (var c = 0; c < res.snapshotLength; c++) {
            tb_tokens[tb_next_token] = res.snapshotItem(c);
            tokens.push(tb_next_token++);
        }
    }
    return tokens.toSource();
}

