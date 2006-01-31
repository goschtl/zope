var livePageUUID;       /* This variable must be defined in your HTML. */
var livePageBaseURL;
var livePageErrors = 0;

function debugEval(str) {
    alert(str);
    eval(str);
}

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
                
            case 'append_comments': {
                var html = lines.join('\n');
                var id = parameter[0];
                alert(cmdline + "Rest:" + html);
                $(id).innerHTML += html;  /* .stripScripts(); */
                /* We must eval all scripts again. Arrgh! */
                $(id).innerHTML.evalScripts();
                return;
                }
                
            case 'append': {
                var html = lines.join('\n');
                var id = parameter[0];
                $(id).innerHTML += html;  /* .stripScripts(); */
                /* We must eval all scripts again. Arrgh! */
                $(id).innerHTML.evalScripts();
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

function checkOutput(outputNum) {
    var base_url = livePageBaseURL + "/@@output/" + livePageUUID;
    var params = "outputNum=" + outputNum;
    
    new Ajax.Request(base_url, 
        { method: 'get',
            parameters: params, 
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
                            setTimeout("checkOutput(0)", 2000);
                            }
                        }
                    else {
                        outputNum += 1
                        setTimeout("checkOutput(" + outputNum + ")", 300);
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
        setTimeout("checkOutput(0)", 500);
        return true;
        }
    else {
        alert("startClient called again...");
        }
}

function idleClient() {
    $("livepage_updates").innerHTML = "idle";
}

function sendLivePage(handler_name, arguments)
{
    var args = "";
    for(i=1;i<arguments.length;i++) {
        args += arguments[i] + ",";
        }
    var base_url = livePageBaseURL + "/@@input/" + livePageUUID;
    var params = "handler_name=" + handler_name + "&arguments=" + args;
  
    new Ajax.Request(base_url, 
        { method: 'get',
            parameters: params
        });
}


function switchElements(a, b) {
    for(i=0;i<$(b).childNodes.length;i++) {
        var child = $(b).childNodes[i];
        $(a).appendChild(child);
        }
        
        
    return true;
}