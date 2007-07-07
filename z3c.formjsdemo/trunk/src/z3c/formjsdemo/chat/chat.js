function mainLoop() {
  var num = $("div.message").length;
  $.get("getMessages", {index: $("div.message").length},
	function(data) {
	  $("#chat-window").append(data);
	  t=setTimeout("mainLoop()", 1000);
	});
}

$(document).ready(function() {
  mainLoop()
})
