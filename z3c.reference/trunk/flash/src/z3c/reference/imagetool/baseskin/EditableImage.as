/**
* z3c.reference.imagetool.baseskin.EditableImage 
* represents a image with a view that can be cropped
*
* @author <gerold.boehler@lovelysystems.com>
*/

import z3c.reference.imagetool.core.*;
import z3c.reference.imagetool.baseskin.*;

[Event("onImageLoaded")]
[Event("onImagePress")]
[Event("onImageRelease")]


class z3c.reference.imagetool.baseskin.EditableImage extends Component
{
    private var MIN_VIEWPORT_SIZE:Number = 20;

    private var image_mc:MovieClip;
    private var fader_mc:MovieClip;
    private var viewport_mc:MovieClip;
    
    private var isDragging:Boolean = false;
    private var isLineDragging:Boolean = false;
    private var isCornerDragging:Boolean = false;
    private var currentDragElement:String = "";
    private var dragElementOffsetX:Number = 0;
    private var dragElementOffsetY:Number = 0;
    private var dragStartPoint:flash.geom.Point;
    private var viewportStartWidth:Number = 1;
    private var viewportStartHeight:Number = 1;
    private var viewportFixedRatio:Number = 1;
    private var viewportStartPoint:flash.geom.Point;
    
    private var mcLoader:MovieClipLoader;

	function EditableImage()
	{
	    super();
	    
	    createEmptyMovieClip("image_mc", getNextHighestDepth());
	    createEmptyMovieClip("fader_mc", getNextHighestDepth());
	    
	    attachMovie("viewport_mc", "viewport_mc", getNextHighestDepth());
	    viewport_mc.addListener(this);
	    
	    mcLoader = new MovieClipLoader();
	    mcLoader.addListener(this);
	    
	    Key.addListener(this);
    }
    
    public function loadImage(url:String)
    {
        mcLoader.loadClip(url, image_mc);
    }

    public function getCropPosition():flash.geom.Point
    {
        return new flash.geom.Point(viewport_mc._x, viewport_mc._y);
    }
    
    public function getCropDimension():flash.geom.Point
    {
        return new flash.geom.Point(viewport_mc._width, viewport_mc._height);
    }

    function onEnterFrame()
    {
        if (FlashvarManager.get("keepAspectRatio") || Key.isDown(Key.SHIFT))
        {
            if (isCornerDragging)
                scaleViewportByRatio();
        }
        else
        {
            if (isLineDragging)
                scaleViewportByLine(_xmouse, _ymouse);

            if (isCornerDragging)
                scaleViewportByCorner(_xmouse, _ymouse);
        }
        
        if (isDragging || isCornerDragging || isLineDragging)
            updateFader();
    }
    
    private function scaleViewportByLine(cursorX:Number, cursorY:Number)
    {
        switch(currentDragElement)
        {
            case "L":
                var dx = -(cursorX - dragStartPoint.x);

                if (viewportStartPoint.x - dx >= 0)
                {
                    viewport_mc._x = viewportStartPoint.x - dx;
                }
                else
                {
                    viewport_mc._x = 0;
                    viewport_mc._width = viewportStartPoint.x + viewportStartWidth;
                    return;
                }

                if (viewportStartWidth + dx >= MIN_VIEWPORT_SIZE)
                {
                    viewport_mc._width = viewportStartWidth + dx;
                }
                else
                {
                    viewport_mc._width = MIN_VIEWPORT_SIZE;
                    viewport_mc._x = viewportStartPoint.x + viewportStartWidth - MIN_VIEWPORT_SIZE;
                    return;
                }

                break;

            case "T":
                var dy = -(cursorY - dragStartPoint.y);

                if (viewportStartPoint.y - dy >= 0)
                {
                    viewport_mc._y = viewportStartPoint.y - dy;
                }
                else
                {
                    viewport_mc._y = 0;
                    viewport_mc._height = viewportStartPoint.y + viewportStartHeight;
                    return;
                }

                if (viewportStartHeight + dy >= MIN_VIEWPORT_SIZE)
                {
                    viewport_mc._height = viewportStartHeight + dy;
                }
                else
                {
                    viewport_mc._height = MIN_VIEWPORT_SIZE;
                    viewport_mc._y = viewportStartPoint.y + viewportStartHeight - MIN_VIEWPORT_SIZE;
                    return;
                }
                break;

                
            case "R":
                var dx = cursorX - dragStartPoint.x;

                if (viewportStartPoint.x + viewportStartWidth + dx >= image_mc._width)
                {
                    viewport_mc._width = image_mc._width - viewportStartPoint.x;
                    return;
                }
                
                if (viewportStartWidth + dx >= MIN_VIEWPORT_SIZE)
                {
                    viewport_mc._width = viewportStartWidth + dx;
                }
                else
                {
                    viewport_mc._width = MIN_VIEWPORT_SIZE;
                }
                break;
                
            case "B":
                var dy = cursorY - dragStartPoint.y;
                
                if (viewportStartPoint.y + viewportStartHeight + dy >= image_mc._height)
                {
                    viewport_mc._height = image_mc._height - viewportStartPoint.y;
                    return;
                }
                
                if (viewportStartHeight + dy >= MIN_VIEWPORT_SIZE)
                {
                    viewport_mc._height = viewportStartHeight + dy;
                }
                else
                {
                    viewport_mc._height = MIN_VIEWPORT_SIZE;
                }
                break;
        }
        
        viewport_mc.updateSensitiveAreas();
    }
    
    private function scaleViewportByCorner(cursorX:Number, cursorY:Number)
    {
        var lines = currentDragElement.split("");
        for (var i = 0; i < lines.length; i++)
        {
            currentDragElement = lines[i];
            scaleViewportByLine(cursorX, cursorY);
        }
        currentDragElement = lines.join("");
    }
    
    private function scaleViewportByRatio()
    {
        switch(currentDragElement)
        {
            case "LT":
                var offsetX = _xmouse - viewportStartPoint.x;
                var offsetY = _ymouse - viewportStartPoint.y;
                var offset = (offsetX < offsetY) ? (offsetX) : (offsetY);
                var cursorX = viewportStartPoint.x + (offset + dragElementOffsetX);
                var cursorY = viewportStartPoint.y + (offset + dragElementOffsetY) / viewportFixedRatio;
                scaleViewportByCorner(cursorX, cursorY);
                break;
            
            case "RT":
                var offsetX = viewportStartPoint.x + viewportStartWidth - _xmouse;
                var offsetY = _ymouse - viewportStartPoint.y;
                var offset = (offsetX < offsetY) ? offsetX : offsetY;
                var cursorX = viewportStartPoint.x + viewportStartWidth - (offset - dragElementOffsetX) / viewportFixedRatio;
                var cursorY = viewportStartPoint.y + (offset + dragElementOffsetY);
                scaleViewportByCorner(cursorX, cursorY);
                break;
                
            case "LB":
                var offsetX = _xmouse - viewportStartPoint.x;
                var offsetY = viewportStartPoint.y + viewportStartHeight - _ymouse;
                var offset = (offsetX < offsetY) ? offsetX : offsetY;
                var cursorX = viewportStartPoint.x + (offset + dragElementOffsetX);
                var cursorY = viewportStartPoint.y + viewportStartHeight - (offset - dragElementOffsetY) / viewportFixedRatio;
                scaleViewportByCorner(cursorX, cursorY);
                break;
            
            case "RB":
                var offsetX = _xmouse - viewportStartPoint.x;
                var offsetY = _ymouse - viewportStartPoint.y;
                var offset = (offsetX > offsetY) ? (offsetX) : (offsetY);
                var cursorX = viewportStartPoint.x + (offset + dragElementOffsetX);
                var cursorY = viewportStartPoint.y + (offset + dragElementOffsetY) / viewportFixedRatio;
                scaleViewportByCorner(cursorX, cursorY);
                break;
        }
    }
    
    private function moveViewportBy(x:Number, y:Number)
    {
        if (viewport_mc._x + x < 0)
            viewport_mc._x = 0;
        else if (viewport_mc._x + x > image_mc._width - viewport_mc._width)
            viewport_mc._x = image_mc._width - viewport_mc._width;
        else
            viewport_mc._x += x;
            
        if (viewport_mc._y + y < 0)
            viewport_mc._y = 0;
        else if (viewport_mc._y + y > image_mc._height - viewport_mc._height)
            viewport_mc._y = image_mc._height - viewport_mc._height;
        else
            viewport_mc._y += y;
        
    }
    
    // event listeners --------------------------------------------------------------

    function onLoadInit(mc:MovieClip)
    {
        viewport_mc.init();
        viewportFixedRatio = FlashvarManager.get("keepAspectRatio") ? (viewport_mc._width / viewport_mc._height) : 1;
        viewport_mc._x = FlashvarManager.get("crop_x");
        viewport_mc._y = FlashvarManager.get("crop_x");
        updateFader();
        
        var ei:EventInfo = new EventInfo(this, "onImageLoaded");
        broadcastEvent(ei);
    }

    function onKeyDown()
    {
        var offset = Key.isDown(Key.SHIFT) ? 5 : 1;
        
        switch(Key.getCode())
        {
            case Key.UP:
                moveViewportBy(0, -offset);
                break;
                
            case Key.DOWN:
                moveViewportBy(0, offset);
                break;
                
            case Key.LEFT:
                moveViewportBy(-offset, 0);
                break;
                
            case Key.RIGHT:
                moveViewportBy(offset, 0);
                break;
                
            case Key.SHIFT:
                if (FlashvarManager.get("keepAspectRatio"))
                {
                    
                }
                else
                {
                    //viewport_mc._x = Math.floor(viewport_mc._x);
                    //viewport_mc._y = Math.floor(viewport_mc._y);
                    //viewport_mc._width = Math.floor(viewport_mc._width);
                    //viewport_mc._height = Math.floor(viewport_mc._height);
                }
                break;
        }
    }
    
    function onMouseDown()
    {
        // first check if the mouse is over the image at all
        if (_xmouse < 0 || _xmouse > _width || _ymouse < 0 || _ymouse > _height)
            return;
            
        // now check if the hit the image
        if (_xmouse >= viewport_mc._x && _xmouse <= viewport_mc._x + viewport_mc._width && 
            _ymouse >= viewport_mc._y && _ymouse <= viewport_mc._y + viewport_mc._height)
                return;
            
        var ei:EventInfo = new EventInfo(this, "onImagePress");
        broadcastEvent(ei);
    }
    
    function onMouseUp()
    {
        //if (_xmouse >= viewport_mc._x && _xmouse <= viewport_mc._x + viewport_mc._width && 
        //    _ymouse >= viewport_mc._y && _ymouse <= viewport_mc._y + viewport_mc._height)
        //        return;

        var ei:EventInfo = new EventInfo(this, "onImageRelease");
        broadcastEvent(ei);
    }
    
    function onViewportPress(ei:EventInfo)
    {
        viewport_mc.startDrag(false, 0, 0, image_mc._width - viewport_mc._width, image_mc._height - viewport_mc._height);
        isDragging = true;
    }
    
    function onViewportRelease(ei:EventInfo)
    {
        viewport_mc.stopDrag();
        viewport_mc._x = Math.floor(viewport_mc._x);
        viewport_mc._y = Math.floor(viewport_mc._y);
        updateFader();
        isDragging = false;
    }
    
    function onLinePress(ei:EventInfo)
    {
        currentDragElement = ei.getInfo("line");
        viewportStartPoint = new flash.geom.Point(viewport_mc._x, viewport_mc._y);
        dragStartPoint = new flash.geom.Point(Math.floor(_xmouse), Math.floor(_ymouse));
        viewportStartWidth = viewport_mc._width;
        viewportStartHeight = viewport_mc._height;
        isLineDragging = true;
    }
    
    function onLineRelease(ei:EventInfo)
    {
        isLineDragging = false;
    }
    
    function onCornerPress(ei:EventInfo)
    {
        currentDragElement = ei.getInfo("corner");
        dragElementOffsetX = ei.getInfo("offsetX");
        dragElementOffsetY = ei.getInfo("offsetY");
        viewportStartPoint = new flash.geom.Point(viewport_mc._x, viewport_mc._y);
        dragStartPoint = new flash.geom.Point(Math.floor(_xmouse), Math.floor(_ymouse));
        viewportStartWidth = viewport_mc._width;
        viewportStartHeight = viewport_mc._height;
        isCornerDragging = true;
    }
    
    function onCornerRelease(ei:EventInfo)
    {
        isCornerDragging = false;
    }
    
    public function onParentResize(w:Number, h:Number)
    {

    }
    
    // helpers ----------------------------------------------------------------------------
    
    private function updateFader()
    {
        fader_mc.clear();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(0, 0);
        fader_mc.lineTo(viewport_mc._x, 0);
        fader_mc.lineTo(viewport_mc._x, viewport_mc._y);
        fader_mc.lineTo(0, viewport_mc._y)
        fader_mc.endFill();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(viewport_mc._x, 0);
        fader_mc.lineTo(viewport_mc._x + viewport_mc._width, 0);
        fader_mc.lineTo(viewport_mc._x + viewport_mc._width, viewport_mc._y);
        fader_mc.lineTo(viewport_mc._x, viewport_mc._y)
        fader_mc.endFill();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(viewport_mc._x + viewport_mc._width, 0);
        fader_mc.lineTo(image_mc._width, 0);
        fader_mc.lineTo(image_mc._width, viewport_mc._y);
        fader_mc.lineTo(viewport_mc._x + viewport_mc._width, viewport_mc._y)
        fader_mc.endFill();
        
        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(0, viewport_mc._y);
        fader_mc.lineTo(viewport_mc._x, viewport_mc._y);
        fader_mc.lineTo(viewport_mc._x, viewport_mc._y + viewport_mc._height);
        fader_mc.lineTo(0, viewport_mc._y + viewport_mc._height)
        fader_mc.endFill();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(viewport_mc._x + viewport_mc._width, viewport_mc._y);
        fader_mc.lineTo(image_mc._width, viewport_mc._y);
        fader_mc.lineTo(image_mc._width, viewport_mc._y + viewport_mc._height);
        fader_mc.lineTo(viewport_mc._x + viewport_mc._width, viewport_mc._y + viewport_mc._height)
        fader_mc.endFill();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(0, viewport_mc._y + viewport_mc._height);
        fader_mc.lineTo(viewport_mc._x, viewport_mc._y + viewport_mc._height);
        fader_mc.lineTo(viewport_mc._x, image_mc._height);
        fader_mc.lineTo(0, image_mc._height)
        fader_mc.endFill();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(viewport_mc._x, viewport_mc._y + viewport_mc._height);
        fader_mc.lineTo(viewport_mc._x + viewport_mc._width, viewport_mc._y + viewport_mc._height);
        fader_mc.lineTo(viewport_mc._x + viewport_mc._width, image_mc._height);
        fader_mc.lineTo(viewport_mc._x, image_mc._height)
        fader_mc.endFill();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(viewport_mc._x + viewport_mc._width, viewport_mc._y + viewport_mc._height);
        fader_mc.lineTo(image_mc._width, viewport_mc._y + viewport_mc._height);
        fader_mc.lineTo(image_mc._width, image_mc._height);
        fader_mc.lineTo(viewport_mc._x + viewport_mc._width, image_mc._height)
        fader_mc.endFill();
    }
}
