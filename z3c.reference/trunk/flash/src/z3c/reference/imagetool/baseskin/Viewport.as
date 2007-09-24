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
    private var current_top_corner:MovieClip;       // save the currently topmost corner
    
    private var dragPointerDegrees:Object;
    
    private var current_pointer_mc:MovieClip;
    
    private var width:Number;
    private var height:Number;
    private var isLocked:Boolean = false;
    
	function Viewport()
	{
	    super();
	    
	    createEmptyMovieClip("drag_area_mc", getNextHighestDepth());
	    initDragArea(drag_area_mc);

	    createEmptyMovieClip("line_left_mc", getNextHighestDepth());
	    initLine(line_left_mc, "L");

	    createEmptyMovieClip("line_right_mc", getNextHighestDepth());
	    initLine(line_right_mc, "R");

	    createEmptyMovieClip("line_top_mc", getNextHighestDepth());
	    initLine(line_top_mc, "T");

	    createEmptyMovieClip("line_bottom_mc", getNextHighestDepth());
	    initLine(line_bottom_mc, "B");
        
	    createEmptyMovieClip("corner_LT", getNextHighestDepth());
	    initCorner(corner_LT, "LT");

	    createEmptyMovieClip("corner_RT", getNextHighestDepth());
	    initCorner(corner_RT, "RT");

	    createEmptyMovieClip("corner_LB", getNextHighestDepth());
	    initCorner(corner_LB, "LB");

	    createEmptyMovieClip("corner_RB", getNextHighestDepth());
	    initCorner(corner_RB, "RB");
	    
	    current_top_corner = corner_RB;
	    
	    dragPointerDegrees = new Object();
	    dragPointerDegrees.L = 90;
	    dragPointerDegrees.R = 270;
	    dragPointerDegrees.T = 180;
	    dragPointerDegrees.B = 0;
	    dragPointerDegrees.LT = 135;
	    dragPointerDegrees.RT = 225;
	    dragPointerDegrees.LB = 45;
	    dragPointerDegrees.RB = 315;
    }
    
    public function setLocked(locked:Boolean)
    {
        isLocked = locked;
        updateDragElements();
    }
    
    public function getLocked():Boolean
    {
        return isLocked;
    }
    
    public function setSize(w:Number, h:Number)
    {
        log("setSize: " + w + " " + h)
        setWidth(w);
        setHeight(h);
    }
    
    public function setWidth(w:Number, ratio:Number)
    {
        width = w;
        if (ratio)
            height = w / ratio;
        
	    updateDragElements();
    }
    
    public function setHeight(h:Number, ratio:Number)
    {
        height = h;
        if (ratio)
            width = h * ratio;
        
	    updateDragElements();
    }
    
    private function updateDragElements()
    {
        drag_area_mc.clear();
        drag_area_mc.lineStyle(0, 0xffffff, 100);
	    drag_area_mc.beginFill(0xabcdef, 0)
	    drag_area_mc.moveTo(0, 0);
	    drag_area_mc.lineTo(width, 0);
	    drag_area_mc.lineTo(width, height);
	    drag_area_mc.lineTo(0, height);
	    drag_area_mc.endFill();
	    
        if (isLocked)
        {
            line_left_mc.clear();
            line_right_mc.clear();
            line_top_mc.clear();
            line_bottom_mc.clear();
        }
        else
        {
    	    drawRectangle(line_left_mc, 0, 0, SENSITIVE_AREA, height);
    	    drawRectangle(line_right_mc, 0, 0, SENSITIVE_AREA, height);
    	    drawRectangle(line_top_mc, 0, 0, width, SENSITIVE_AREA);
    	    drawRectangle(line_bottom_mc, 0, 0, width, SENSITIVE_AREA);
        }

        line_left_mc._x = 0;
        line_left_mc._y = 0;

        line_right_mc._x = width - line_right_mc._width;
        line_right_mc._y = 0;

        line_top_mc._x = 0;
        line_top_mc._y = 0;

        line_bottom_mc._x = 0;
        line_bottom_mc._y = height - line_bottom_mc._height;

        drawRectangle(corner_LT, 0, 0, 2*SENSITIVE_AREA, 2*SENSITIVE_AREA, 0xffffff, 100);
        drawRectangle(corner_RT, 0, 0, 2*SENSITIVE_AREA, 2*SENSITIVE_AREA, 0xffffff, 100);
        drawRectangle(corner_LB, 0, 0, 2*SENSITIVE_AREA, 2*SENSITIVE_AREA, 0xffffff, 100);
        drawRectangle(corner_RB, 0, 0, 2*SENSITIVE_AREA, 2*SENSITIVE_AREA, 0xffffff, 100);

        corner_LT._x = 0;
        corner_LT._y = 0;
        
        corner_RT._x = width - corner_RT._width;
        corner_RT._y = 0;
        
        corner_LB._x = 0;
        corner_LB._y = height - corner_LB._height;
        
        corner_RB._x = width - corner_RB._width;
        corner_RB._y = height - corner_RB._height;
    }
    
    // event listeners --------------------------------------------------------------
    
    function onViewportRatioChange(ei:EventInfo)
    {
        var ratio = ei.getInfo("ratio");
        isLocked = !!ratio;
        updateDragElements()
    }
    
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

    function onDragElementRollOver(element_mc:MovieClip)
    {
        current_pointer_mc = _level0.imagetool_mc.mousepointer_mc.pointer_corner_mc;
        onEnterFrame();
        Mouse.hide();
        current_pointer_mc._rotation = dragPointerDegrees[element_mc.type];
        current_pointer_mc._visible = true;
    }
    
    function onDragElementRollOut(line:MovieClip)
    {
        current_pointer_mc._visible = false;
        current_pointer_mc = null;
        Mouse.show();
    }
    
    function onDragElementPress(element_mc:MovieClip)
    {
        var type = element_mc.type;
        var ei:EventInfo = new EventInfo(this, "onDragElementPress");
        ei.setInfo("type", type);
        
        if (type == "LT")
        {
            ei.setInfo("dragStartX", _x + element_mc._x);
            ei.setInfo("dragStartY", _y + element_mc._y);
            current_top_corner.swapDepths(element_mc);
            current_top_corner = element_mc;
        }
        else if (type == "RT")
        {
            ei.setInfo("dragStartX", _x + element_mc._x + element_mc._width);
            ei.setInfo("dragStartY", _y + element_mc._y);
            current_top_corner.swapDepths(element_mc);
            current_top_corner = element_mc;
        }
        else if (type == "LB")
        {
            ei.setInfo("dragStartX", _x + element_mc._x);
            ei.setInfo("dragStartY", _y + element_mc._y + element_mc._height);
            current_top_corner.swapDepths(element_mc);
            current_top_corner = element_mc;
        }
        else if (type == "RB")
        {
            ei.setInfo("dragStartX", _x + element_mc._x + element_mc._width);
            ei.setInfo("dragStartY", _y + element_mc._y + element_mc._height);
            current_top_corner.swapDepths(element_mc);
            current_top_corner = element_mc;
        }
        else if (type == "L")
        {
            ei.setInfo("dragStartX", _x + element_mc._x)
        }
        else if (type == "R")
        {
            ei.setInfo("dragStartX", _x + element_mc._x + element_mc._width)
        }
        else if (type == "T")
        {
            ei.setInfo("dragStartY", _y + element_mc._y)
        }
        else if (type == "B")
        {
            ei.setInfo("dragStartY", _y + element_mc._y + element_mc._height)
        }

        broadcastEvent(ei);
    }
    
    function onDragElementRelease(element_mc:MovieClip)
    {
        onDragElementRollOut();
            
        var ei:EventInfo = new EventInfo(this, "onDragElementRelease");
        broadcastEvent(ei);
    }

    function onEnterFrame()
    {
        if (current_pointer_mc)
        {
            current_pointer_mc._x = _level0._xmouse;
            current_pointer_mc._y = _level0._ymouse;
        }
    }
    
    // helpers ----------------------------------------------------------------------------
    
    private function drawRectangle(mc:MovieClip, x:Number, y:Number, w:Number, h:Number, color:Number, alpha:Number)
    {
        color = color ? color : 0xffffff;
        alpha = alpha ? alpha : 0;
	    mc._x = x;
	    mc._y = y;
	    mc.clear();
	    mc.beginFill(color, alpha)
	    mc.moveTo(0, 0);
	    mc.lineTo(w, 0);
	    mc.lineTo(w, h);
	    mc.lineTo(0, h);
	    mc.endFill();
    }
    
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
        line_mc.type = line;
        line_mc._alpha = 100;
        line_mc.useHandCursor = false;
	    line_mc.onRollOver = function() { _parent.onDragElementRollOver(this); }
	    line_mc.onRollOut = function() { _parent.onDragElementRollOut(this); }
        line_mc.onPress = function() { _parent.onDragElementPress(this); }
        line_mc.onRelease = line_mc.onReleaseOutside = function() { _parent.onDragElementRelease(this); }
    }
    
    private function initCorner(corner_mc:MovieClip, corner:String)
    {
        corner_mc.type = corner;
        corner_mc._alpha = 100;
        corner_mc.useHandCursor = false;
	    corner_mc.onRollOver = function() { _parent.onDragElementRollOver(this); }
	    corner_mc.onRollOut = function() { _parent.onDragElementRollOut(this); }
        corner_mc.onPress = function() { _parent.onDragElementPress(this); }
        corner_mc.onRelease = corner_mc.onReleaseOutside = function() { _parent.onDragElementRelease(this); }
    }
}
