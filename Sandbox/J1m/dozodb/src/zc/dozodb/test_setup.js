
var last_xhr;

function pprint(pname, ob, indent) {
    var print = ! indent, out = [], i, name, names;

    if (! indent) {
        indent = pname ? '  ' : '';
    }
    if (pname) {
        out.push(pname+': ');
    }
    else {
        out.push(indent);
    }
    if (dojo.isArray(ob)) {
        if (ob.length == 0) {
            out.push('[]');
        }
        else {
            out.push('[\n');
            for(i = 0; i < ob.length; i++) {
                out.push(pprint('', ob[i], indent+'  '));
                out.push(',\n');
            }
            out.pop();
            out.push(' ]');
        }
    }
    else if (dojo.isFunction(ob) || ! ob || ! dojo.isObject(ob)) {
        out.push(dojo.toJson(ob));
    }
    else {
        names = [];
        for (name in ob) {
            if (ob.hasOwnProperty(name)) {
                names.push(name);
            }
        }
        if (names.length == 0)
            out.push('{}');
        else {
            names.sort();
            if (pname) {
                out.push('{\n');
                i = indent+'  ';
            }
            else {
                out.push('{');
                i = ' ';
            }
            dojo.forEach(
                names, function (name) {
                    out.push(i);
                    out.push(pprint(name, ob[name], indent+'  '));
                    i = indent+'  ';
                    out.push(',\n');
                });
            out.pop();
            out.push(' }');
            }
    }
    out = out.join('');
    if (print) {
        console.log(out);
        return undefined;
    }
    return out;
}

dojo.xhr = function (method, args, hasBody) {
    var i, name, nonfun={};
    last_xhr = {};
    for (name in args) {
        if (args.hasOwnProperty(name)) {
            if (typeof args[name] == 'function') {
                last_xhr[name] = args[name];
            }
            else {
                nonfun[name] = args[name];
            }
        }
    }
    pprint('xhr '+method, nonfun);
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

function assert(cond, message) {
    if (! cond) {
        console.error('Assertion Failed: '+message);
    }
}
