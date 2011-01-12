/*

 Copyright (c) 2011 Zope Foundation and Contributors.
 All Rights Reserved.

 This software is subject to the provisions of the Zope Public License,
 Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
 THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
 WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
 FOR A PARTICULAR PURPOSE.

*/

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

var last_xhr;

dojo.objectToQuery = function (ob) { // simple minded impl :)
    var name, result = [];
    for (name in ob) {
        if (ob.hasOwnProperty(name)) {
            result.push(name+'='+ob[name]);
        }
    }
    return result.join('&');
};

dojo.xhr = function (method, args, hasBody) {
    last_xhr = args;
    if (args.content) {
        if (typeof args.content !== 'string') {
            args.content = dojo.objectToQuery(args.content);
        }
        if (method == 'GET') {
            args.url += '?' + args.content;
        }
    }
    pprint('xhr '+method, args);
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

var xhr_respond = function(json) {
    last_xhr.load(dojo.fromJson(json));
};

function assert(cond, message) {
    if (! cond) {
        console.error('Assertion Failed: '+message);
    }
}
