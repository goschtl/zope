/**
* z3c.reference.imagetool.baseskin.Viewport 
* represents cropped area
*
* @author <gerold.boehler@lovelysystems.com>
*/

import z3c.reference.imagetool.core.*;
import z3c.reference.imagetool.baseskin.*;


class z3c.reference.imagetool.baseskin.Viewport extends Component
{
    private var SENSITIVE_AREA:Number = 5;
    
    private var drag_area_mc:MovieClip;
    
    private var line_left_mc:MovieClip;
    private var line_right_mc:MovieClip;
    private var line_top_mc:MovieClip;
    private var line_bottom_mc:MovieClip;
    
    private var corner_LT:MovieClip;
    private var corner_RT:MovieClip;
    private var corner_LB:MovieClip;
    private var corner_RB:MovieClip;
    
    private var linePointerDegrees:Object;
    private var cornerPointerDegrees:Object;
    
    private var current_pointer_mc:MovieClip;
    
	function Viewport()
	{
	    super();
	    
	    createEmptyMovieClip("drag_area_mc", getNextHighestDepth());
	    initDragArea(drag_area_mc);

        if (!FlashvarManager.get("keepAspectRatio"))
        {
    	    createEmptyMovieClip("line_left_mc", getNextHighestDepth());
    	    initLine(line_left_mc, "L");

    	    createEmptyMovieClip("line_right_mc", getNextHighestDepth());
    	    initLine(line_right_mc, "R");

    	    createEmptyMovieClip("line_top_mc", getNextHighestDepth());
    	    initLine(line_top_mc, "T");

    	    createEmptyMovieClip("line_bottom_mc", getNextHighestDepth());
    	    initLine(line_bottom_mc, "B");
        }
        
	    createEmptyMovieClip("corner_LT", getNextHighestDepth());
	    initCorner(corner_LT, "LT");

	    createEmptyMovieClip("corner_RT", getNextHighestDepth());
	    initCorner(corner_RT, "RT");

	    createEmptyMovieClip("corner_LB", getNextHighestDepth());
	    initCorner(corner_LB, "LB");

	    createEmptyMovieClip("corner_RB", getNextHighestDepth());
	    initCorner(corner_RB, "RB");
	    
	    linePointerDegrees = new Object();
	    linePointerDegrees.L = 90;
	    linePointerDegrees.R = 270;
	    linePointerDegrees.T = 180;
	    linePointerDegrees.B = 0;
	    
	    cornerPointerDegrees = new Object();
	    cornerPointerDegrees.LT = 135;
	    cornerPointerDegrees.RT = 225;
	    cornerPointerDegrees.LB = 45;
	    cornerPointerDegrees.RB = 315;
    }
    
    public function init()
    {
        var w = FlashvarManager.get("crop_w");
        var h = FlashvarManager.get("crop_h");
        
        drag_area_mc.clear();
        drag_area_mc.lineStyle(0, 0xc0c0c0, 100);
	    drag_area_mc.beginFill(0xff0000, 0);
	    drag_area_mc.moveTo(0, 0);
	    drag_area_mc.lineTo(w, 0);
	    drag_area_mc.lineTo(w, h);
	    drag_area_mc.lineTo(0, h);
	    drag_area_mc.endFill();
	    
	    redrawSensitiveAreas(w, h, SENSITIVE_AREA);
	    repositionSensitiveAreas(w, h);
    }
    
    public function updateSensitiveAreas(maxW:Number, maxH:Number)
    {
        /*
        var dx = _width - FlashvarManager.get("crop_w");
        var dy = _height - FlashvarManager.get("crop_h");
        var dxMax = maxW - FlashvarManager.get("crop_w");
        var dyMax = maxH - FlashvarManager.get("crop_h");
        var scaleX = 1 - dx / dxMax;
        var scaleY = 1 - dy / dxMax;
        */
        //redrawSensitiveAreas(maxW, maxH, SENSITIVE_AREA);
	    //redrawSensitiveAreas(_width, _height, SENSITIVE_AREA);
	    //repositionSensitiveAreas(_width, _height);
    }
    
    private function redrawSensitiveAreas(w:Number, h:Number, size:Number)
    {
        if (!FlashvarManager.get("keepAspectRatio"))
        {
    	    drawRectangle(line_left_mc, 0, 0, size, h);
    	    drawRectangle(line_right_mc, 0, 0, size, h);
    	    drawRectangle(line_top_mc, 0, 0, w, size);
    	    drawRectangle(line_bottom_mc, 0, 0, w, size);
        }

        drawRectangle(corner_LT, 0, 0, 2*size, 2*size);
        drawRectangle(corner_RT, 0, 0, 2*size, 2*size);
        drawRectangle(corner_LB, 0, 0, 2*size, 2*size);
        drawRectangle(corner_RB, 0, 0, 2*size, 2*size);
    }
    
    private function repositionSensitiveAreas(w:Number, h:Number)
    {
        if (!FlashvarManager.get("keepAspectRatio"))
        {
            line_left_mc._x = 0;
            line_left_mc._y = 0;

            line_right_mc._x = w - line_right_mc._width;
            line_right_mc._y = 0;

            line_top_mc._x = 0;
            line_top_mc._y = 0;

            line_bottom_mc._x = 0;
            line_bottom_mc._y = h - line_bottom_mc._height;
        }

        corner_LT._x = 0;
        corner_LT._y = 0;
        
        corner_RT._x = w - corner_RT._width;
        corner_RT._y = 0;
        
        corner_LB._x = 0;
        corner_LB._y = h - corner_LB._height;
        
        corner_RB._x = w - corner_RB._width;
        corner_RB._y = h - corner_RB._height;
    }
    
    private function drawRectangle(mc:MovieClip, x:Number, y:Number, w:Number, h:Number)
    {
	    mc._x = x;
	    mc._y = y;
	    mc.clear();
	    mc.beginFill(0x0000ff, 100)
	    mc.moveTo(0, 0);
	    mc.lineTo(w, 0);
	    mc.lineTo(w, h);
	    mc.lineTo(0, h);
	    mc.endFill();
    }
    
    // event listeners --------------------------------------------------------------
    
    function onDragAreaRollOver(area:MovieClip)
    {
        current_pointer_mc = _level0.imagetool_mc.mousepointer_mc.pointer_drag_mc;
        onEnterFrame();
        Mouse.hide();
        current_pointer_mc._visible = true;
    }
    
    function onDragAreaRollOut(area:MovieClip)
    {
        current_pointer_mc._visible = false;
        current_pointer_mc = null;
        Mouse.show();
    }
    
    function onDragAreaPress(area:MovieClip)
    {
        var ei:EventInfo = new EventInfo(this, "onViewportPress");
        broadcastEvent(ei);
    }
    
    function onDragAreaRelease(area:MovieClip)
    {
        var ei:EventInfo = new EventInfo(this, "onViewportRelease");
        broadcastEvent(ei);
    }
    
    function onLineRollOver(line_mc:MovieClip)
    {
        current_pointer_mc = _level0.imagetool_mc.mousepointer_mc.pointer_line_mc;
        onEnterFrame();
        Mouse.hide();
        current_pointer_mc._rotation = linePointerDegrees[line_mc.line] + _parent._rotation;
        current_pointer_mc._visible = true;
    }
    
    function onLineRollOut(line:MovieClip)
    {
        current_pointer_mc._visible = false;
        current_pointer_mc = null;
        Mouse.show();
    }
    
    function onLinePress(line_mc:MovieClip)
    {
        var ei:EventInfo = new EventInfo(this, "onLinePress");
        ei.setInfo("line", line_mc.line);

        switch(line_mc.line)
        {
            case "L":
                ei.setInfo("offsetX", line_mc._xmouse);
                ei.setInfo("offsetY", 0);
                break;
                
            case "R":
                ei.setInfo("offsetX", -(line_mc._width - line_mc._xmouse));
                ei.setInfo("offsetY", 0);
                break;
                
            case "T":
                ei.setInfo("offsetX", 0);
                ei.setInfo("offsetY", line_mc._ymouse);
                break;
                
            case "B":
                ei.setInfo("offsetX", 0);
                ei.setInfo("offsetY", -(line_mc._height - line_mc._ymouse));
                break;
        }        

        broadcastEvent(ei);
    }
    
    function onLineRelease(line_mc:MovieClip)
    {
        if (!line_mc.hitTest(_level0._xmouse, _level0._ymouse, true))
            onLineRollOut();
            
        var ei:EventInfo = new EventInfo(this, "onLineRelease");
        broadcastEvent(ei);
    }
    
    function onCornerRollOver(corner_mc:MovieClip)
    {
        current_pointer_mc = _level0.imagetool_mc.mousepointer_mc.pointer_corner_mc;
        onEnterFrame();
        Mouse.hide();
        current_pointer_mc._rotation = cornerPointerDegrees[corner_mc.corner] + _parent._rotation;
        current_pointer_mc._visible = true;
    }
    
    function onCornerRollOut(line:MovieClip)
    {
        current_pointer_mc._visible = false;
        current_pointer_mc = null;
        Mouse.show();
    }
    
    function onCornerPress(corner_mc:MovieClip)
    {
        var ei:EventInfo = new EventInfo(this, "onCornerPress");
        ei.setInfo("corner", corner_mc.corner);
        
        switch(corner_mc.corner)
        {
            case "LT":
                ei.setInfo("offsetX", corner_mc._xmouse);
                ei.setInfo("offsetY", corner_mc._ymouse);
                break;
                
            case "RT":
                ei.setInfo("offsetX", -(corner_mc._width - corner_mc._xmouse));
                ei.setInfo("offsetY", corner_mc._ymouse);
                break;
                
            case "LB":
                ei.setInfo("offsetX", corner_mc._xmouse);
                ei.setInfo("offsetY", -(corner_mc._height - corner_mc._ymouse));
                break;
                
            case "RB":
                ei.setInfo("offsetX", -(corner_mc._width - corner_mc._xmouse));
                ei.setInfo("offsetY", -(corner_mc._height - corner_mc._ymouse));
                break;
        }
        
        broadcastEvent(ei);
    }
    
    function onCornerRelease(corner_mc:MovieClip)
    {
        if (!corner_mc.hitTest(_level0._xmouse, _level0._ymouse, true))
            onCornerRollOut();
            
        var ei:EventInfo = new EventInfo(this, "onCornerRelease");
        broadcastEvent(ei);
    }
    
    function onEnterFrame()
    {
        if (current_pointer_mc)
        {
            //Mouse.hide();
            current_pointer_mc._x = _level0._xmouse;
            current_pointer_mc._y = _level0._ymouse;
        }
        else
        {
            /*
            if (this.hitTest(_level0._xmouse, _level0._ymouse, true))
                Mouse.hide();
            else
                Mouse.show();
            */
        }
            
    }
    
    public function onParentResize(w:Number, h:Number)
    {

    }
    
    // helpers ----------------------------------------------------------------------------
    
    private function initDragArea(area_mc:MovieClip)
    {
        area_mc.useHandCursor = false;
        area_mc.onRollOver = function() { _parent.onDragAreaRollOver(this); }
        area_mc.onRollOut = function() { _parent.onDragAreaRollOut(this); }
        area_mc.onPress = function() { _parent.onDragAreaPress(this); }
        area_mc.onRelease = area_mc.onReleaseOutside = function() { _parent.onDragAreaRelease(this); }
    }
    
    private function initLine(line_mc:MovieClip, line:String)
    {
        line_mc.line = line;
        line_mc._alpha = 0;
        line_mc.useHandCursor = false;
	    line_mc.onRollOver = function() { _parent.onLineRollOver(this); }
	    line_mc.onRollOut = function() { _parent.onLineRollOut(this); }
        line_mc.onPress = function() { _parent.onLinePress(this); }
        line_mc.onRelease = line_mc.onReleaseOutside = function() { _parent.onLineRelease(this); }
    }
    
    private function initCorner(corner_mc:MovieClip, corner:String)
    {
        corner_mc.corner = corner;
        corner_mc._alpha = 0;
        corner_mc.useHandCursor = false;
	    corner_mc.onRollOver = function() { _parent.onCornerRollOver(this); }
	    corner_mc.onRollOut = function() { _parent.onCornerRollOut(this); }
        corner_mc.onPress = function() { _parent.onCornerPress(this); }
        corner_mc.onRelease = corner_mc.onReleaseOutside = function() { _parent.onCornerRelease(this); }
    }
}
