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
    return top.frames[0].document.documentElement.innerHTML;
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
    links = top.frames[0].document.getElementsByTagName('a');
    var id = _tb_remembered_links.length
    _tb_remembered_links[id] = links[info[0]];
    return id;
}

function _tb_clickRememberedLink(info) {
    var n = info[0];
    var element = _tb_remembered_links[n];
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

