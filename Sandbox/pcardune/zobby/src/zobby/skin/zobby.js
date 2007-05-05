function roundCorners(element){
  $(element).wrap('<div class="dialog"><div class="bd">'+
		  '<div class="c"><div class="s"></div></div></div></div>');
  $('div.dialog')
    .prepend('<div class="hd">'+
	     '<div class="c"></div></div>')
    .append('<div class="ft">'+
	    '<div class="c"></div></div>');
}