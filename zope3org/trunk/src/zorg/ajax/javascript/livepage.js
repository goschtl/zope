
var livePageClientId;       /* This variable must be defined in your HTML. */
                                 
function evalResponse(request) {
    var response = request.responseText;
    
    var lines = response.split(/\n/);
    var cmdline = lines.shift();
    var parameter = cmdline.split(" ");
    var cmd = parameter.shift();
    
    switch(cmd) {
        case 'update': {
            var body = lines.join('\n');
            id = parameter[0];
            $(id).innerHTML = body;
            return;
            }
        case 'javascript' : {
            var expr = parameter.join(" ");
            eval(expr);
            return;
            }
        }
}

function checkOutput(outputNum) {
    var base_url = "./@@livepageoutput";
    var params = "livepage_client=" + livePageClientId + "&outputNum=" + outputNum;
    
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
