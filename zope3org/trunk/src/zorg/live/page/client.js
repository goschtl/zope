var livePageUUID;       /* This variable must be defined in your HTML. */
var livePageBaseURL;
var livePageErrors = 0;

function debugEval(str) {
    alert(str);
    eval(str);
}

var userAgent = navigator.userAgent.toLowerCase();

function evalResponse(request) {
    var response = request.responseText;
    
    if (response) {
        var lines = response.split(/\n/);
        var cmdline = lines.shift();
        var parameter = cmdline.split(" ");
        var cmd = parameter.shift();

        switch(cmd) {
        
            case 'reload' : {
                alert("The connection has been interrupted. The page will be reloaded.");
                window.location.reload();
                }
                
            case 'update': {
                var html = lines.join('\n');
                var id = parameter[0];
                $(id).innerHTML = html;  /* .stripScripts(); */
                html.evalScripts();
                return;
                }
      
            case 'append': {
                var html = lines.join('\n');
                var id = parameter[0];
                var act = parameter[1];
                $(id).innerHTML += html;  /* .stripScripts(); */
                /* We must eval all scripts again. Arrgh!   */
                $(id).innerHTML.evalScripts();

                if (act) {
                    switch(act) {
                        case 'scroll' : {
                            scrollToLast(id);
                            return;
                            }
                        case 'sound' : {
                            playFlash("ping");
                            return;
                            }
                        }
                    }
                return;
                }
                
            case 'update_src': {
                var id = parameter[0];
                $(id).src = parameter[1];
                return;
                }
                
            case 'javascript' : {
                var expr = parameter.join(" ");
                eval(expr);
                return;
                }
                
            case 'idle': {
                return;
                }
        }
        
        alert("Error:" + response);
        livePageErrors += 1;
    }   
}

function checkOutput() {
    var base_url = livePageBaseURL + "/@@output/" + livePageUUID;
    
    new Ajax.Request(base_url, 
        { method: 'get',
            asynchronous:true,
            onError : function(request) { alert('Output error'); },
            onComplete: function(request) { 
                    evalResponse(request); 
                    if (livePageErrors > 3) {
                        alert("Too much errors. The page will be reloaded.");
                        window.location.reload();
                        }
                    else if (livePageErrors > 1) {
                        if (confirm('An error occured. Reload page?')) {
                            window.location.reload();
                            }
                        else {
                            setTimeout("checkOutput()", 2000);
                            }
                        }
                    else {
                        setTimeout("checkOutput()", 500);
                        }
                }
        });
}
         
function startClient() {
    if (!livePageBaseURL) {
        livePageBaseURL = window.location.href;
        var i = livePageBaseURL.indexOf('#');
        if (i != -1) {
            livePageBaseURL = livePageBaseURL.substring(0, i);
            }
        setTimeout("checkOutput()", 500);
        return true;
        }
    else {
        alert("startClient called again...");
        }
}

function stopClient() {
    sendEvent("close", { uuid: livePageUUID });
}

function idleClient() {
    $("livepage_updates").innerHTML = "idle";
}

function sendEvent(verb, args)
{
    var params = "verb=" + verb;
    for(key in args) {
        params += "&" + key + "=" + args[key]
        }
    var base_url = livePageBaseURL + "/@@input/" + livePageUUID;
    
    new Ajax.Request(base_url, 
        { method: 'post',
            parameters: params
        });
    }

function scrollToLast(id) {
    var area = $(id);
    if (area.offsetHeight > area.scrollHeight) {
        area.scrollTop = 0;
    } else {
        area.scrollTop = area.scrollHeight;
    }
};

