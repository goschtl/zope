var jsonrpc = imprt("jsonrpc");
var pythonkw = imprt("pythonkw");
var address=".";
var server=null;
var connected=false;
var session=null;
var running=false;

function connect(){
  if (server == null){
    try{server = new jsonrpc.ServiceProxy(address, ["testConnection",
						    "connectUser",
						    "disconnectUser",
						    "newSession",
						    "getSessions"]);
    }catch(e){alert(e);}
    var username = $("#connectUsername").attr("value");
    server.connectUser(username,
		       function(result, err){
      $("#message").html(result);
      $("#connectUsername").attr("disabled", true);
      $("#connectButton")
	.attr("value", "Disconnect")
	.unbind("click")
	.click(disconnect);
      ping();
      getSessions();
    });
  }
}

function disconnect(){
  server.disconnectUser($("#connectUsername").attr("value"),
			function(result, err){
    $("#message").html(result);
    $("#connectUsername").attr("disabled", false);
    $("#connectButton")
      .attr("value", "Connect")
      .unbind("click")
      .click(connect);
  });
}

function ping(){
  server.testConnection(pingCallback)
}
function pingCallback(resp, err){
  if (!err){
    connected=true;
    $("#status").html(resp);
  }
  else{
    connected=false;
    $("#status").html(''+err);
  }
}

function joinSession(name){
  session = null;
  $("#chatbox").html("");
  try{session = new jsonrpc.ServiceProxy(address+'/'+name, ["testConnection",
							    "sendChat","getChatMessages"]);
  }catch(e){alert(e);}
  session.testConnection(function(result,err){
    $("#workspaceMessage").html(result);
    $("#workspace").show();
    if (running == false){
      runSessionLoop();
    }
  });
}

function closeSession(){
  session=null;
}

function runSessionLoop(){
  running = true;
  updateChatMessages();
  ping();
  if (session){
    t=setTimeout("runSessionLoop()",1000);
  }
}

function sendChatMessage(event){
  if (event.which != 13){ return null; }

  session.sendChat(new pythonkw.PythonKw({'message': $('#chatInput').attr('value'),
                                         'index': $('#chatbox div').length}),
    function(result, err){
      $("#chatInput").attr('value','');
    })
}

function updateChatMessages(){
  session.getChatMessages($("#chatbox div").length,
    function (result, err){
      $.each(result, function(i, value){
          $("#chatbox").prepend($("<div></div>").html(value));
      });      
  });
}

function getSessions(){
  server.getSessions(function (result,err){
    $("#sessions").html("");
    $.each(result,function(i,name){
      link = $('<input type="button" />').attr("value", name);
      link.click(function(){joinSession(name); return null;});
      $("<li></li>").html(link).appendTo("#sessions");
    })
  });
}

function createNewSession(){
  server.newSession($("#newSessionName").attr('value'), function(result,err){
    $("#message").html(result);
    getSessions();
  });
}

function initializeApp(){
  $("#connectButton").click(connect);
  $("#newSession").click(createNewSession);
  $("#sendChatInput").click(sendChatMessage);
  $("#chatInput").keydown(sendChatMessage);
  $("#workspace").hide();
}


$(document).ready(function() {
   initializeApp();
   roundCorners("#insideWrapper");
 });
