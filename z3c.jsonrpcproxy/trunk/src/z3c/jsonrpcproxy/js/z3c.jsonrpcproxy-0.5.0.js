//----------------------------------------------------------------------------
/** 
 * @fileoverview JSON-RPC client implementation 
 * @author Roger Ineichen dev at projekt01 dot ch
 * @version 0.6, supports JSON-RPC 1.0, 1.1 and 2.0
 */
//----------------------------------------------------------------------------

function JSONRPC(url, version) {
    this._url = url;
    // uses specification version 2.0 by default
    this._version = '2.0'
    if (typeof(version) != 'undefined') {
        this._version = version;
    }
    this._methods = new Array();
    this._user = null;
    this._password = null;
}

function getJSONRPCProxy(url, version) {
    return new JSONRPC(url, version);
}

JSONRPC.prototype.addMethod = function(name, callback, requestId) {
    if (typeof(requestId) == 'undefined') {
        requestId = "jsonRequest";
    }
    var self = this;
    if(!self[name]){
        var method = new JSONRPCMethod(this._url, name, callback, requestId, this._user, this._password, this._version);
        self[name] = method;
        this._methods.push(method);
    }
}

JSONRPC.prototype.setAuthentication = function(user, pass) {
    this._user = user;
    this._password = pass;
    for(var i=0;i<this._methods.length;i++){
        this._methods[i].setAuthentication(user, pass);
    }
}

function JSONRPCMethod(url, methodName, callback, requestId, user, pass, version) {
    this.methodName = methodName;
    this.callback = callback;
    this.requestId = requestId;
    this.url = url;
    this.user = user;
    this.password = pass;
    this.version = version
    var self = this;

    var fn = function(){
        var oldVersion = false;
        if (this.version == '1.0' || this.version == '1.1') {
            oldVersion = true;
        }
        if (!oldVersion && arguments.length == 1 && typeof arguments[0] === "object"){
            // we've got version 2.0 and an associative array as argument
            var args = arguments[0]
        } else {
            // we've got positional arguments
            var args = new Array();
            for(var i=0;i<arguments.length;i++){
                args.push(arguments[i]);
            }
        }
        if(self.callback) {
            var data = self.jsonRequest(self.requestId, self.methodName, args);
            self.postData(self.url, self.user, self.password, data, function(resp){
                var res = null;
                var exc = null;
                try{
                    res = self.handleResponse(resp);
                }catch(e){
                    exc = e;
                }
                try{
                    callback(res, self.requestId, exc);
                }catch(e){
                    alert("callback method error: " + e.message);
                }
                args = null;
                resp = null;
            });
        }
        else{
            var data = self.jsonRequest(self.requestId, self.methodName, args);
            var resp = self.postData(self.url, self.user, self.password, data);
            return self.handleResponse(resp);
        }
    }
    return fn;
}

JSONRPCMethod.prototype.postData = function(url, user, pass, data, callback) {
    var xmlhttp = new XMLHttp(url);
    var header = new Array()
    header["Content-Type"] = "application/json";
    xmlhttp.setHeaders(header);
    xmlhttp.user = user;
    xmlhttp.password = pass;
    xmlhttp.argString = data;
    if(callback == null){
        return xmlhttp.post();
    }else{
        xmlhttp.post(callback);
    }
}

JSONRPCMethod.prototype.jsonRequest = function(id, methodName, args){
    var ji = toJSON(id);
    var jm = toJSON(methodName);
    var ja = toJSON(args);
    var ver = this.version
    if (ver == '1.0'){
        return '{"id":' +ji+ ', "method":' +jm+ ', "params":' +ja+ "}";
    }else if (ver == '1.1'){
        return '{"version":"'+ver+'", "id":' +ji+ ', "method":' +jm+ ', "params":' +ja+ "}";
    }else{
        return '{"jsonrpc":"'+ver+'", "id":' +ji+ ', "method":' +jm+ ', "params":' +ja+ "}";
    }
}

JSONRPCMethod.prototype.setAuthentication = function(user, pass){
    this.user = user;
    this.password = pass;
}

JSONRPCMethod.prototype.notify = function(){
    var args=new Array();
    for(var i=0;i<arguments.length;i++){
        args.push(arguments[i]);
    }
    var data = this.jsonRequest(null, this.methodName, args);
    this.postData(this.url, this.user, this.password, data, function(resp){});
}

JSONRPCMethod.prototype.handleResponse = function(resp){
    // TODO: Implement better error handling support since we have error codes 
    // offer an argument xmlhttp.onError which defines a function for custom 
    // error handling.
    var status=null;
    try{
        status = resp.status;
    }catch(e){
    }
    if(status == 200){
        var respTxt = "";
        try{
            respTxt=resp.responseText;
        }catch(e){
        }
        if(respTxt == null || respTxt == ""){
            alert("The server responded with an empty document.");
        }else{
            var res = this.unmarshall(respTxt);
            var oldVersion = false;
            if (this.version == '1.0' || this.version == '1.1') {
                oldVersion = true;
            }
            if(oldVersion  && res.error != null){
                alert(res.error);
            }
            else if(!oldVersion  && res.error != null){
                alert(res.error.message);
            }
            else if (res.requestId != self.requestId) {
                alert("wrong json id returned");
            }
            else{
                return res.result;
            }
        }
    }else{
        alert("error " + status);
    }
}

JSONRPCMethod.prototype.unmarshall = function(source){
    try {
        var obj;
        eval("obj=" + source);
        return obj;
    }catch(e){
        alert("The server's response could not be parsed.");
    }
}

function escapeJSONChar(c) {
    if(c == "\"" || c == "\\") return "\\" + c;
    else if (c == "\b") return "\\b";
    else if (c == "\f") return "\\f";
    else if (c == "\n") return "\\n";
    else if (c == "\r") return "\\r";
    else if (c == "\t") return "\\t";
    var hex = c.charCodeAt(0).toString(16);
    if(hex.length == 1) return "\\u000" + hex;
    else if(hex.length == 2) return "\\u00" + hex;
    else if(hex.length == 3) return "\\u0" + hex;
    else return "\\u" + hex;
}

function escapeJSONString(s) {
    var parts = s.split("");
    for(var i=0; i < parts.length; i++) {
	var c =parts[i];
	if(c == '"' ||
	   c == '\\' ||
	   c.charCodeAt(0) < 32 ||
	   c.charCodeAt(0) >= 128)
	    parts[i] = escapeJSONChar(parts[i]);
    }
    return "\"" + parts.join("") + "\"";
}

function toJSON(o) {
    if(o == null) {
    	return "null";
    } else if(o.constructor == String) {
	    return escapeJSONString(o);
    } else if(o.constructor == Number) {
	    return o.toString();
    } else if(o.constructor == Boolean) {
	    return o.toString();
    } else if(o.constructor == Date) {
	    return o.valueOf().toString();
    } else if(o.constructor == Array) {
    	var v = [];
    	for(var i = 0; i < o.length; i++) v.push(toJSON(o[i]));
    	return "[" + v.join(", ") + "]";
    }
    else {
    	var v = [];
    	for(attr in o) {
    	    if(o[attr] == null) v.push("\"" + attr + "\": null");
    	    else if(typeof o[attr] == "function"); // skip
    	    else v.push(escapeJSONString(attr) + ": " + toJSON(o[attr]));
    	}
    	return "{" + v.join(", ") + "}";
    }
}
