var livePageUUID;       /* This variable must be defined in your HTML. */
 
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
            case 'update': {
                var html = lines.join('\n');
                var id = parameter[0];
                $(id).innerHTML = html.stripScripts();
                html.evalScripts();
                return;
                }
                
            case 'append': {
                var html = lines.join('\n');
                var id = parameter[0];
                 $(id).innerHTML += html.stripScripts();
                html.evalScripts();
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
        }
    }
}

function checkOutput(outputNum) {
    var base_url = "./@@livepageoutput";
    var params = "uuid=" + livePageUUID + "&outputNum=" + outputNum;
    
    new Ajax.Request(base_url, 
        { method: 'get',
            parameters: params, 
            asynchronous:true, 
            onComplete: function(request) { evalResponse(request); checkOutput(outputNum+1); }
        });
}
         
function startClient() {
    setTimeout("checkOutput(0)", 500);
    return true;
}

function idleClient() {
    $("livepage_updates").innerHTML = "idle";
}

function switchElements(a, b) {
    for(i=0;i<$(b).childNodes.length;i++) {
        var child = $(b).childNodes[i];
        $(a).appendChild(child);
        }
        
        
    return true;
}