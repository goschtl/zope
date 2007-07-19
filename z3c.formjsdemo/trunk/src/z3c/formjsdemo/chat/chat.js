function mainLoop() {
  var num = $("div.message").length;
  $.get("@@index.html/@@ajax/getMessages", {index: $("div.message").length},
	function(data) {
	  $("#chat-window").append(data);
	  $("#chat-window").get(0).scrollTop = $("#chat-window").get(0).scrollHeight;
	  t=setTimeout("mainLoop()", 1000);
	});
}

$(document).ready(function() {
  mainLoop()
})
