var tb_tokens = {};
var tb_next_token = 0;

tb_page_loaded = false;
document.getElementById("appcontent"
    ).addEventListener("load", function() { tb_page_loaded = true; }, true);

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
            //alert(tb_normalize_whitespace(a.textContent) + '|' + text + '|' + tb_normalize_whitespace(a.textContent).indexOf(text));
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
    return tb_get_link_by_predicate(
        function (a) {
            alert(a.id + '|' + id + '|' + (a.id == id));
            return a.id == id;
        }, index)
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
