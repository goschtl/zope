last_result = '__testbrowser__no_result_yet';
should_stop = false;
_tb_onloadFunc = function() {};

function _tb_gotNextCommand(info) {
    log('gotNextCommand');
    var command = info[0];
    log(command);
    last_result = eval(info[0] + '(' + info[1] + ')');
    if (last_result == '_tb_WAIT_FOR_PAGE_LOAD') {
        _tb_waitForLoad(_tb_nextCommand);
    } else if (!should_stop) {
        _tb_nextCommand();
    }
}

function _tb_waitForLoad(func) {
    log('waiting');
    _tb_onloadFunc = function() {
        log('loaded');
        _tb_onloadFunc = function() {};
        func();
    }
}

function _tb_fetchNextCommandFailed(error) {
    alert(error);
}

function _tb_nextCommand() {
    if (should_stop) {
        return
    }
    var req = getXMLHttpRequest();
    req.open('POST', '/__api__/next');
    var d = sendXMLHttpRequest(req, serializeJSON(last_result)+'\r\n');
    last_result = undefined;
    d.addCallback(evalJSONRequest);
    d.addCallback(_tb_gotNextCommand);
    d.addErrback(_tb_fetchNextCommandFailed);
}

connect(window, 'onload', _tb_nextCommand);
