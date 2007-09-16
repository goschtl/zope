Stage.align = "LT";
Stage.scaleMode = "noScale";
		
		
// Debug Block Start
if (System.capabilities.playerType == "External"){
    if (!_level0.url) _level0.url="testimage.jpg";
    
    //default values
    if (!_level0.crop_x) _level0.crop_x = 100;
    if (!_level0.crop_y) _level0.crop_y = 100;
    if (!_level0.crop_w) _level0.crop_w = 100;
    if (!_level0.crop_h) _level0.crop_h = 100;
    if (!_level0.original_w) _level0.original_w = 600;
    if (!_level0.original_h) _level0.original_h = 400;
    //if (!_level0.output_w) _level0.output_w = 200;
    //if (!_level0.output_h) _level0.output_h = 50;
    if (!_level0.zoomfactor) _level0.zoomfactor=0.33;
    if (!_level0.rotation) _level0.rotation=90;
}
// Debug Block End


// create an instance of the z3c Image Tool
var tool:ImageTool = ImageTool(_root.attachMovie("BaseClip","BaseClip", _root.getNextHighestDepth()));

tool.setOutputSize(parseInt(_level0.output_w), parseInt(_level0.output_h));
tool.setOriginalSize(parseInt(_level0.original_w), parseInt(_level0.original_h));
tool.setCrop(parseInt(_level0.crop_x), parseInt(_level0.crop_y), parseInt(_level0.crop_w), parseInt(_level0.crop_h));
tool.setUrl(_level0.url);
tool.setRotation(parseInt(rotation)*-1); //PIL rotates opposite to flash
tool.setOutputRatio(parseFloat(_level0.zoomfactor));
tool.initialize();
stop();



