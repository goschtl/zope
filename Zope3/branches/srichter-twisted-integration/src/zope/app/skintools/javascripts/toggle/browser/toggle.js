//----------------------------------------------------------------------------
// toggle boxes
//
// toggle expand/collapse named blocks
// register own toggle icons in your layer if needed
//----------------------------------------------------------------------------

//----------------------------------------------------------------------------
// public API
//----------------------------------------------------------------------------                      
function toggle(img, node) {
  var target = document.getElementById(node);
  if (target.style.display == "none") {
    target.style.display = "block";
    img.src = collapseGif;
  } else {
    target.style.display = "none";
    img.src = expandGif;
  }
}

// TODO: improve it
// use preferrences and xmlhttp for store toggle stat persistent.
