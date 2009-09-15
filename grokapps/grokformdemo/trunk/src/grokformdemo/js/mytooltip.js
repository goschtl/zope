$(document).ready(function() {

    $("#form :input").tooltip({ 
        position: "center right", 
        offset: [-2, 10], 
        effect: "fade", 
        opacity: 0.7, 
        tip: '.tooltip' 
    });

    $("#form :input").blur(function() {
          var value = $(this).val();
          var id = $(this).attr('id')
          var url = window.location + '/@@validate'
          console.log("input value, %s  ", value);
          console.log("input id, %s  ", id);
          console.log(window.location)
          $.getJSON(url,
                   {'value':value, 'id':id},
                   function(data){ 
                       console.log(data); 
                       message = data.message;
                       id = data.id;
                       console.log(message);
                       console.log(id);
                       $("div#"+id).toggleClass('errored-field'); 
                       $("div#"+id+"_help").append(message); 
                       console.log("HELL");
                       })
         
 
        
    });
});
