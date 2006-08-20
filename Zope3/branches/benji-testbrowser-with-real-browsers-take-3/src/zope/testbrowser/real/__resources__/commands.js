_tb_remembered_links = [];

function log(msg) {
//    top.frames['log_frame'].document.write(msg + '<br />');
}

function _tb_open(info) {
    selenium.doOpen(info[0]);
    selenium.doWaitForPageToLoad(10000);
}

function _tb_stop(info) {
    should_stop = true;
}

function _tb_getContents(info) {
    temp = document.createElement('div');
    clone = top.frames[0].document.documentElement.cloneNode(true);
    temp.appendChild(clone);
    contents=temp.innerHTML;
    temp.innerHTML="";
    return contents;
}

function _tb_getUrl(info) {
    return selenium.getLocation().href;
}

function _tb_reload(info) {
    top.frames[0].location = top.frames[0].location.href;
    return '_tb_WAIT_FOR_PAGE_LOAD';
}

function _tb_goBack(info) {
    top.frames[0].history.back();
    return '_tb_WAIT_FOR_PAGE_LOAD';
}

function _tb_rememberLinkN(info) {
    function getElementsByTagNames(names, obj) {
        var results = [];
        if (obj == undefined) {
            var obj = document;
        }

        for (var i=0; i<names.length; i++) {
            var elements = obj.getElementsByTagName(names[i]);
            for (var j=0; j<elements.length; j++) {
                results.push(elements[j]);
            }
        }

        var testNode = results[0];
        if (!testNode) return [];
        if (testNode.sourceIndex) {
            results.sort(function (a,b) {
                return a.sourceIndex - b.sourceIndex;
            });
        }
        else if (testNode.compareDocumentPosition) {
            results.sort(function (a,b) {
                return 3 - (a.compareDocumentPosition(b) & 6);
            });
        }
        return results;
    }

    var links = getElementsByTagNames(['a', 'area'], top.frames[0].document);
    var id = _tb_remembered_links.length;
    _tb_remembered_links[id] = links[info[0]];
    return id;
}

function _tb_setControlValue(info) {
    log(info);
    var form_index = info[0];
    var control_index = info[1];
    var value = info[2];
    var doc = top.frames[0].document;
    var element = doc.forms[form_index][control_index];
    element.value = value; // XXX need to handle different ways of setting value
}

function locateElementByRememberdLink(locator, doc) {
    var n = Number(locator);
    return _tb_remembered_links[n];
}

function _tb_clickRememberedLink(info) {
    selenium.doClick('rememberedlink=' + info[0]);
}

//function _tb_doEvent(element, type) {
//    if (element.fireEvent) {
//        element.fireEvent('on'+type);
//    } else {
//        var evt = document.createEvent('HTMLEvents');
//        evt.initEvent(type, false, true);
//        element.dispatchEvent(evt);
//    }
//}

function _tb_click(e) {
    if (e.onclick) {
        log('using onclick');
        e.onclick();
    }
    else {
        log('using href');
        log(e.href);
        top.frames[0].location = e.href;
    }
}

