function log(msg) {
    top.frames['log_frame'].document.write(msg + '<br />');
}

function _tb_open(info) {
    log('open '+info[0]);
    _tb_remembered_links = [];
    top.frames[0].location = info[0];
    return '_tb_WAIT_FOR_PAGE_LOAD';
}

function _tb_stop(info) {
    should_stop = true;
    top.frames['log_frame'].document.close();
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
    return top.frames[0].location.href;
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
    function getElementsByTagNames(tagNames,obj) {
        if (!obj) var obj = document;
        var resultArray = new Array();
        for (var i=0;i<tagNames.length;i++) {
            var tags = obj.getElementsByTagName(tagNames[i]);
            for (var j=0;j<tags.length;j++) {
                resultArray.push(tags[j]);
            }
        }
        var testNode = resultArray[0];
        if (!testNode) return [];
        if (testNode.sourceIndex) {
            resultArray.sort(function (a,b) {
                return a.sourceIndex - b.sourceIndex;
            });
        }
        else if (testNode.compareDocumentPosition) {
            resultArray.sort(function (a,b) {
                return 3 - (a.compareDocumentPosition(b) & 6);
            });
        }
        return resultArray;
}
//    function getElementsByTagNames(names, node) {
//        var results = [];
//        for (var i in names) {
//            var tags = node.getElementsByTagName(names[i]);
//            for (var j in tags) {
//                results.push(tags[j]);
//            }
//        }
//        var example = results[0];

//        if (!example) return [];

//        if (example.sourceIndex) {
//            results.sort(function (a,b) {return a.sourceIndex - b.sourceIndex;});
//        }
//        else if (example.compareDocumentPosition) {
//            results.sort(function (a,b) {
//                return 3 - (a.compareDocumentPosition(b) & 6);
//            });
//        }
//        return results;
//    }

    log(info);
    var links = getElementsByTagNames(['a', 'area'], top.frames[0].document);
    var id = _tb_remembered_links.length;
    _tb_remembered_links[id] = links[info[0]];
    log(links.length);
    log(id);
    log(_tb_remembered_links[id]);
    return id;
}

function _tb_clickRememberedLink(info) {
    log(info);
    var n = info[0];
    var element = _tb_remembered_links[n];
    log(element);
    _tb_click(element);
    return '_tb_WAIT_FOR_PAGE_LOAD';
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

