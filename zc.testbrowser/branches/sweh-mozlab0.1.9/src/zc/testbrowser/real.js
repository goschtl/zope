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

function tb_xpath_tokens(pattern, contextToken) {
    var tokens = new Array();
    var context = null;
    if (contextToken != null) {
        context = tb_tokens[contextToken]
    }
    var result = tb_xpath(pattern, context);
    var debug_tokens = new Array();
    for (var c = 0; c < result.snapshotLength; c++) {
        tb_tokens[tb_next_token] = result.snapshotItem(c);
        debug_tokens.push(tb_tokens[tb_next_token].tagName);
        tokens.push(tb_next_token++);
    }
    return tokens;
}

function tb_extract_token_attrs(tokens, attr) {
    var attrs = new Array();
    for (var i in tokens) {
        attrs.push(tb_tokens[tokens[i]].getAttribute(attr));
    }
    return attrs;
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

    var height = content.innerHeight + content.scrollMaxY;
    var width = content.innerWidth + content.scrollMaxX;

    canvas.width = width;
    canvas.height = height;

    var ctx = canvas.getContext('2d');
    ctx.drawWindow(content, 0, 0, width, height, 'rgb(0,0,0)');
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

function tb_click_token(token, client_x, client_y) {
    var a = tb_tokens[token];
    var evt = a.ownerDocument.createEvent('MouseEvents');
    if (client_x == null) client_x = 0;
    if (client_y == null) client_y = 0;
    evt.initMouseEvent('click', true, true, a.ownerDocument.defaultView,
        1, 0, 0, client_x, client_y, false, false, false, false, 0, null);
    a.dispatchEvent(evt);
}

function tb_follow_link(token) {
    tb_click_token(token);
    // empty the tokens data structure, they're all expired now
    // XXX: justas: really? what about links which do not lead from the page
    // and are only used for javascript onclick event?
    tb_tokens = {};
}

function tb_set_checked(token, checked) {
    var input = tb_tokens[token];
    var tagName = input.tagName;
//  XXX: yes, it would be nice to handle checkbox checking via mouse events, but
//  sometimes tests run too fast, and Firefox misses the mouse clicks
//    var changed = false;
//    if ((input.checked && !checked) || (!input.checked && checked))
//        changed = true;
//    if (changed) {
//        var evt = input.ownerDocument.createEvent('MouseEvents');
//        evt.initMouseEvent('click', true, true,
//                           input.ownerDocument.defaultView,
//                           1, 0, 0, 0, 0, false, false, false, false,
//                           0, null);
//        input.dispatchEvent(evt);
//    }
    if (tagName == 'OPTION') {
        input.selected = checked;
    }
    else {
        input.checked = checked;
        type = input.getAttribute('type');
        value = input.getAttribute('value')
        if (type == 'checkbox' && value == null) {
            input.setAttribute('value', 'on');
        }
    }
}

function tb_get_checked(token) {
    var input = tb_tokens[token];
    var tagName = input.tagName;
    if (tagName == 'OPTION') {
        return input.selected;
    }
    return input.checked;
}

function tb_get_link_text(token) {
    return tb_normalize_whitespace(tb_tokens[token].textContent);
}

function tb_get_control_by_predicate(
    predicate, index, allowDuplicate, context, xpath) {
    if (xpath == null) {
        var xpath = './/input | .//select | .//option | .//textarea';
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
                if (tag == 'INPUT' &&
                    control.getAttribute('type').toUpperCase() == 'SUBMIT') {
                    labelText = control.getAttribute('value');
                }

                var id = control.getAttribute('id');
                var name = control.getAttribute('name');
                // The label encloses the input element
                var res = tb_xpath("ancestor::label", control);
                // The label element references the control id
                if (res.snapshotLength == 0) {
                    var res = tb_xpath("//label[@for='" + id + "']")
                }
                // Collect all text content, since HTML allows multiple labels
                // for the same input.
                if (res.snapshotLength > 0) {
                    if (!labelText) {
                        labelText = '';
                    }
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

function tb_get_control_by_name(name, index, contextToken, xpath) {
    return tb_get_control_by_predicate(
        function (control) {
            var controlName = control.getAttribute('name');
            return controlName != null && controlName == name;
        }, index, true, tb_tokens[contextToken], xpath)
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
    } else if (tagName == 'INPUT') {
        var elemName = elem.getAttribute('name');
        var typeName = elem.getAttribute('type');
        var res = tb_xpath("//input[@name='" + elemName +
                           "'][@type='"+typeName+"']", elem);
        for (var c = 0; c < res.snapshotLength; c++) {
            var item = res.snapshotItem(c);
            var value = item.getAttribute('value');
            if (value != null && value != 'on') {
                options.push(item.getAttribute('value'));
            }
            else {
                options.push(true);
            }
        }
    }
    return options;
}

function tb_get_listcontrol_displayOptions(token) {
    var elem = tb_tokens[token];
    var tagName = elem.tagName;
    var options = new Array();
    if (tagName == 'SELECT') {
        var res = tb_xpath('child::option', elem)
        for (var c = 0; c < res.snapshotLength; c++) {
            var item = res.snapshotItem(c)
            if (item.hasAttribute('label'))
                options.push(item.getAttribute('label'))
            else
                options.push(item.textContent);
        }
    } else if (tagName == 'INPUT') {
        var elemName = elem.getAttribute('name');
        var typeName = elem.getAttribute('type');
        var res = tb_xpath("//input[@name='" + elemName +
                           "'][@type='"+typeName+"']", elem);
        for (var c = 0; c < res.snapshotLength; c++) {
            var item = res.snapshotItem(c);
            labels = tb_find_labels(item);
            for (var i = 0; i < labels.length; i++) {
                options.push(labels[i]);
            }
        }
    }

    return options;
}

function tb_act_as_single(token) {
    elem = tb_tokens[token]
    tagName = elem.tagName
    if (tagName == 'INPUT') {
        typeName = elem.getAttribute('type');
        var elem = tb_tokens[token];
        var res = tb_xpath("//input[@name='" + elem.getAttribute('name') +
                           "'][@type='"+typeName+"']", elem);
        if (res.snapshotLength > 1) {
            return false;
        }
        else if (res.snapshotLength == 1) {
            item = res.snapshotItem(0);
            return !item.hasAttribute('value');
        }
        return true;
    }
    return false;
}

function tb_is_listcontrol_multiple(token) {
    elem = tb_tokens[token]
    tagName = elem.tagName
    if (tagName == 'SELECT') {
        multiple = elem.getAttribute('multiple')
        return (multiple && multiple.toUpperCase() == 'MULTIPLE') ? true : false
    }
    else if (tagName == 'INPUT') {
        var typeName = elem.getAttribute('type');
        if (typeName == 'radio') {
            return false;
        }
        else if (typeName == 'checkbox'){
            var elem = tb_tokens[token];
            var res = tb_xpath("//input[@name='" + elem.getAttribute('name') +
                               "'][@type='"+typeName+"']", elem);
            return res.snapshotLength > 0;
        }
    }
    return false;
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
                values.push(item.getAttribute('value'));
        }
    } else if (tagName == 'INPUT') {
        var elemName = elem.getAttribute('name');
        var typeName = elem.getAttribute('type');
        var res = tb_xpath("//input[@name='" + elemName +
                           "'][@type='"+typeName+"']", elem);
        for (var c = 0; c < res.snapshotLength; c++) {
            var item = res.snapshotItem(c);
            if (item.checked) {
                if (!item.hasAttribute('value'))
                    values.push(true);
                else
                    values.push(item.getAttribute('value'));
            }
        }
    }
    return values;
}

function tb_find_labels(elem) {
    var elem_id = elem.id;
    var labels = new Array();
    // The label encloses the input element
    var res = tb_xpath("ancestor::label", elem);
    // The label element references the control id
    if (res.snapshotLength == 0) {
        var res = tb_xpath("//label[@for='" + elem_id + "']")
    }
    // Collect all text content, since HTML allows multiple labels
    // for the same input.
    if (res.snapshotLength > 0) {
        for (var c = 0; c < res.snapshotLength; c++) {
            labels.push(tb_normalize_whitespace(
                res.snapshotItem(c).textContent));
        }
    }
    return labels;
}

function tb_get_listcontrol_displayValue(token) {
    var elem = tb_tokens[token];
    var tagName = elem.tagName;
    var options = new Array();
    if (tagName == 'SELECT') {
        var res = tb_xpath('child::option', elem)
        for (var c = 0; c < res.snapshotLength; c++) {
            var item = res.snapshotItem(c);
            if (item.selected) {
                if (item.hasAttribute('label'))
                    options.push(item.getAttribute('label'));
                else
                    options.push(item.textContent);
            }
        }
    } else if (tagName == 'INPUT') {
        var elemName = elem.getAttribute('name');
        var typeName = elem.getAttribute('type');
        var res = tb_xpath("//input[@name='" + elemName +
                           "'][@type='"+typeName+"']", elem);
        for (var c = 0; c < res.snapshotLength; c++) {
            var item = res.snapshotItem(c);
            if (item.checked) {
                labels = tb_find_labels(item);
                for (var i = 0; i < labels.length; i++) {
                    options.push(labels[i]);
                }
            }
        }
    }
    return options;
}

function tb_find_listcontrol_elements(token) {
    var elem = tb_tokens[token];
    var tagName = elem.tagName;
    var elements = new Array();
    if (tagName == 'SELECT') {
        var res = tb_xpath('child::option', elem);
        for (var c = 0; c < res.snapshotLength; c++) {
            elements.push(res.snapshotItem(c));
        }
    } else if (tagName == 'INPUT') {
        var elemName = elem.getAttribute('name');
        var typeName = elem.getAttribute('type');
        var res = tb_xpath("//input[@name='" + elemName +
                           "'][@type='"+ typeName +"']");
        for (var c = 0; c < res.snapshotLength; c++) {
            elements.push(res.snapshotItem(c));
        }
    }
    return elements;
}


function tb_set_listcontrol_displayValue(token, value) {
    var elem = tb_tokens[token];
    var tagName = elem.tagName;
    if (tagName == 'SELECT') {
        var res = tb_xpath('child::option', elem)
        for (var c = 0; c < res.snapshotLength; c++) {
            var item = res.snapshotItem(c);
            if (value.indexOf(item.textContent) != -1
                || value.indexOf(item.getAttribute('label')) > -1)
                item.selected = true;
            else
                item.selected = false;
        }
    } else if (tagName == 'INPUT') {
        elements = tb_find_listcontrol_elements(token);
        for (var c = 0; c < elements.length; c++ ) {
            element = elements[c];
            var check = false;
            labels = tb_find_labels(element);
            for (var li = 0; li < labels.length; li++ ) {
                if(value.indexOf(labels[li]) > -1 || value == labels[li]) {
                    check = true;
                }
            }
            element.checked = check;
        }
    }
}

function tb_set_listcontrol_value(token, value) {
    var elem = tb_tokens[token];
    var tagName = elem.tagName;
    if (tagName == 'SELECT') {
        var res = tb_xpath('child::option', elem)
        for (var c = 0; c < res.snapshotLength; c++) {
            var item = res.snapshotItem(c);
            if (value.indexOf(item.getAttribute('value')) != -1)
                item.selected = true;
            else
                item.selected = false;
        }
    }
    else if (tagName == 'INPUT'){
        var elements = tb_find_listcontrol_elements(token);
        for (var c = 0; c < elements.length; c++ ) {
            var element = elements[c];
            var elemValue = element.getAttribute('value');
            if (elemValue != null &&
                (elemValue == value || value.indexOf(elemValue) > -1)) {
                element.checked = true;
            }
            else {
                element.checked = false;
            }
        }
    }
}

function tb_get_listcontrol_item_tokens(token) {
    var tokens = new Array();
    var elements = tb_find_listcontrol_elements(token);
    for (var c = 0; c < elements.length; c++) {
        tb_tokens[tb_next_token] = elements[c];
        tokens.push(tb_next_token++);
    }
    return tokens;
}

function tb_get_contents() {
    // get doctype
    var node = content.document.firstChild;
    var contents = '';
    while (node) {
      if (node.nodeType == node.DOCUMENT_TYPE_NODE) {
        contents += '<!DOCTYPE ' + node.name.toLowerCase() + ' PUBLIC "' +
          node.publicId + '" "' + node.systemId + '">\n';
      } else if (node.nodeType == node.ELEMENT_NODE) {
        var name = node.nodeName.toLowerCase();
        contents += '<' + name + '>\n' + node.innerHTML + '</' + name + '>';
      }
      node = node.nextSibling;
    }
    return contents;
}
