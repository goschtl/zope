//---[ adding menu ]-----------------------------------------------------------
$.fn.hoverClass = function(c) {
    return this.each(function(){
        $(this).hover( 
            function() {$(this).addClass(c);},
            function() {$(this).removeClass(c);}
        );
    });
};

$(document).ready(function(){
    $(".addingMenu li").hover(
        function(){ $("ul", this).fadeIn("fast"); }, 
        function() { } 
    );
    if (document.all) {
        $("#addingMenu li").hoverClass ("addingMenuHover");
    }
});


$(document).ready(function(){
    $('#appMenuContainer').z3cDivMenu();
    $('#addMenu').z3cDivMenu();
    // setup z3c.jsontree based trees
    $('.z3cJSONTree').z3cJSONTree();
});
