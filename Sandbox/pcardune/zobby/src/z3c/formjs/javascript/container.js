var jsonrpc = imprt("jsonrpc");
var pythonkw = imprt("pythonkw");
var address=".";

try{container = new jsonrpc.ServiceProxy(address, ["getAttributes"]);
}catch(e){alert(e);}

