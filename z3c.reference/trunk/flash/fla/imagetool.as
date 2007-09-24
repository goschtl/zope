/*
 * imagetool.as - #include file
 *
 * parameters:
 * 
 * url:                         path to the image to be loaded
 * crop_x:                      crop start x position
 * crop_y:                      crop start y position
 * crop_w:                      crop area width
 * crop_h:                      crop area height
 * min_w:                       minimum width the cropped area must have
 * min_h:                       minimum height the cropped area must have
 * rotation:                    rotation of the image (0, 90, 180, 270)
 * presets:                     list of available ratios, passed as json string 
 *                              example: [{"name": "widescreen", "value": "16:9"}, {"name": "tv", "value": "4:3"}]
 * 
 */


stop();

Stage.align = "LT";
Stage.scaleMode = "noScale";
_focusrect = false;

// Debug Block Start
if (System.capabilities.playerType == "External")
{
    if (!_level0.url) _level0.url="toothbrush.jpg";
    
    //default values
    if (_level0.crop_x == undefined) _level0.crop_x = 1440;
    if (_level0.crop_y == undefined) _level0.crop_y = 880;
    if (_level0.crop_w == undefined) _level0.crop_w = 400;
    if (_level0.crop_h == undefined) _level0.crop_h = 400;
    if (_level0.rotation == undefined) _level0.rotation = 0;
    if (_level0.presets == undefined) _level0.presets = '[{"name": "Freehand"}, {"name": "Ratio", "ratio": "4:3"}]';//, {"name": "Output", "output_w": 123, "output_h": 321}, {"name": "Min", "min_w": 222, "min_h": 111}, {"name": "Max", "max_w": 555, "max_h": 444}, {"name": "MinMax", "output_w": 987, "output_h": 654, "max_w": 543, "max_h": 432, "min_w": 432, "min_h": 321}]';
}
// Debug Block End

// bugfix for dropdown
dropdown_mc._lockroot = true;
dropdown_mc._visible = false;
dropdown_mc._alpha = 0;

// init flashvar manager
z3c.reference.imagetool.core.FlashvarManager.collectFlashVars();

// create an instance of the z3c Image Tool
attachMovie("imagetool_mc", "imagetool_mc", getNextHighestDepth())

// bring dropdown to front
dropdown_mc.swapDepths(imagetool_mc);