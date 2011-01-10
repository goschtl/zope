
var last_xhr;

dojo.xhr = function (method, args, hasBody) {
    var i, name, aa=[];
    last_xhr = {};
    for (name in args) {
        if (args.hasOwnProperty(name)) {
            if (typeof args[name] == 'function') {
                last_xhr[name] = args[name];
            }
            else {
                aa.push([name, args[name]]);
            }
        }
    }
    aa.sort();
    console.log("xhr "+method);
    for (i=0; i < aa.length; i++) {
        console.log("  "+aa[i][0]+': '+aa[i][1]);
    }
    if (hasBody ? method !== 'POST' : method !== 'GET') {
        console.error('Bad hasBody: '+ hasBody);
    }
};
dojo.xhrGet = function (args) {
    return dojo.xhr("GET", args);
};
dojo.xhrPost = function (args) {
    return dojo.xhr("POST", args, true);
};


