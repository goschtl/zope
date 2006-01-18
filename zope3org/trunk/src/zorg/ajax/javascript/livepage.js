var livePageClientId;       /* This variable must be defined in your HTML. */
 
livepageScriptFragmentMatch = /<script.*?>((?:\n|.)*?)<\/script>/img;
livepageScriptTags = /<script.*?>|<\/script>/img;

livepageImageFragmentMatch = /<img.+src[ ]*=[ ]*\"(.*?)\"/img;
livepageImageTag = /<img.+src[ ]*=[ ]*\"|\"(?:\n|.)*?\/>/

function evalResponse(request) {
    var response = request.responseText;
    if (response) {
        var lines = response.split(/\n/);
        var cmdline = lines.shift();
        var parameter = cmdline.split(" ");
        var cmd = parameter.shift();
        
        switch(cmd) {
            case 'update': {
                var body = lines.join('\n');
                var id = parameter[0];
                
                var scripts = body.match(livepageScriptFragmentMatch);
               
                if (scripts) {
                    var script = scripts.join('');
                    script = script.replace(livepageScriptTags, '');
                
                    $(id).innerHTML = body;
                    eval(script);
                    }
                else {
                    $(id).innerHTML = body;
                    }
               
                return;
                }
                
            case 'update': {
                var body = lines.join('\n');
                var id = parameter[0];
                
                var scripts = body.match(livepageScriptFragmentMatch);
               
                if (scripts) {
                    var script = scripts.join('');
                    script = script.replace(livepageScriptTags, '');
                
                    $(id).innerHTML = body;
                    eval(script);
                    }
                else {
                    $(id).innerHTML = body;
                    }
               
                return;
                }
                
            
            case 'update_map': {
                var body = lines.join('\n');
                var id = parameter[0];
                $(id).src = parameter[1];
                var map_id = parameter[2];
                var map_name = parameter[3];
                var map = $(map_id);
                map.innerHTML = body;
               
                $(id).usemap = "#" + map_name;
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