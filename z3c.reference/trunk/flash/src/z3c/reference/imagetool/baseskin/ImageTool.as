/**
* z3c.reference.imagetool.baseskin.ImageTool 
* is a tool for cropping and rotating images
*
* @author <gerold.boehler@lovelysystems.com>
*/

import flash.geom.*;
import z3c.reference.imagetool.core.*;
import z3c.reference.imagetool.baseskin.*;

import com.robertpenner.easing.*;
import de.alex_uhlmann.animationpackage.animation.Alpha;


class z3c.reference.imagetool.baseskin.ImageTool extends Component
{
    private var PADDING:Number = 10;
    private var MIN_VIEWPORT_SIZE:Number = 10;

    private var canvas_mc:MovieClip;
    private var editable_image_mc:MovieClip;
    private var fader_mc:MovieClip;
    private var viewport_mc:MovieClip;
    private var mousepointer_mc:MovieClip;
    private var controller_mc:MovieClip;
    private var preloader_mc:MovieClip;
    
    private var dragStartPoint:Point;
    private var isViewportDragging:Boolean = false;
    private var isElementDragging:Boolean = false;
    private var currentDragElement:String = "";

    private var dragCursorStart:Point;
    private var dragImageStart:Point;
    private var isDraggingImage:Boolean = false;
    
    private var viewportStartPoint:Point;
    private var viewportStartSize:Point;
    private var viewportFixedRatio:Number = 1;
    private var viewportOutputSize:Point;
    private var viewportMinSize:Point;
    private var viewportMaxSize:Point;
    
    private var imageAttitude:EditableImageAttitude;
    private var imageMinMaxDelta:Point;

    private var animAlphaOut:Alpha;
    private var animAlphaIn:Alpha;
    
    private var currentPercent:Number = 0;
    private var currentPreset;
    
    private var changesLoaded:Boolean = false;
    
	function ImageTool()
	{
	    super();

	    // parse the preset list if available
	    var presets = FlashvarManager.get("presets");
	    // json wants "" not ''
	    presets = presets.split("'").join("\"");
	    if (presets)
	    {
    	    try
    	    {
    	        var presets = org.json.Json.parse(presets);
    	        FlashvarManager.set("presets", presets);
    		}
    		catch (ex)
    		{
    			log("problem in parsing:" + ex.name + ":" + ex.message + ":" + ex.at + ":" + ex.text);
    		}
	    }
	    
	    attachMovie("canvas_mc", "canvas_mc", getNextHighestDepth(), {_alpha: 0});

	    attachMovie("editable_image_mc", "editable_image_mc", getNextHighestDepth());
	    editable_image_mc.addListener(this);
	    editable_image_mc.setMask(canvas_mc.getMask());
	    editable_image_mc._alpha = 0;

	    createEmptyMovieClip("fader_mc", getNextHighestDepth());

        attachMovie("viewport_mc", "viewport_mc", getNextHighestDepth(), {_visible: false, _alpha: 0});
	    viewport_mc.addListener(this);
	    viewport_mc.setMask(canvas_mc.getMask());
	    
	    createEmptyMovieClip("mousepointer_mc", getNextHighestDepth());
	    mousepointer_mc.attachMovie("pointer_drag_mc", "pointer_drag_mc", mousepointer_mc.getNextHighestDepth(), {_visible: false});
	    mousepointer_mc.attachMovie("pointer_line_mc", "pointer_line_mc", mousepointer_mc.getNextHighestDepth(), {_visible: false});
	    mousepointer_mc.attachMovie("pointer_corner_mc", "pointer_corner_mc", mousepointer_mc.getNextHighestDepth(), {_visible: false});	    
	    
	    attachMovie("controller_mc", "controller_mc", getNextHighestDepth(), {_visible: false, _alpha: 0});
	    controller_mc.addListener(this);
	    controller_mc.addListener(viewport_mc);
	    addListener(controller_mc);
	    
	    attachMovie("preloader_mc", "preloader_mc", getNextHighestDepth(), {_x:Stage.width/2, _y:Stage.height/2});
	    
	    animAlphaOut = new Alpha(preloader_mc);
	    animAlphaOut.animationStyle(300, Sine.easeInOut);

	    animAlphaIn = new Alpha([editable_image_mc, controller_mc, viewport_mc, canvas_mc, _level0.dropdown_mc]);
	    animAlphaIn.animationStyle(300, Sine.easeInOut);
	    
        Stage.addListener(this);
	    Key.addListener(this);

        onEnterFrame = initAfterFirstFrame;        
    }
    
    function initAfterFirstFrame()
    {
        editable_image_mc.loadImage(FlashvarManager.get("url"));
        onEnterFrame = onEnterFrameUpdateViewport;
    }
    
    // saving - loading -----------------------------------------------------------------
    
	function saveChanges()
	{
        // then get the scale factor for the output values
        var finalScale = imageAttitude.originalWidth / imageAttitude.w;
        var finalImageW = imageAttitude.originalWidth;
        var finalImageH = imageAttitude.originalHeight;
        var finalImageR = imageAttitude.r;
        var finalCropX = (viewport_mc._x - imageAttitude.x) * finalScale;
        var finalCropY = (viewport_mc._y - imageAttitude.y) * finalScale;
        var finalViewportW = viewport_mc._width * finalScale;
        var finalViewportH = viewport_mc._height * finalScale;
        
        // if a output size is defined, apply it
        var outputW = viewportOutputSize.x;
        var outputH = viewportOutputSize.y;
        var outputScale = 1;
        if (outputW)
            outputScale = outputW / finalViewportW;
        else if (outputH)
            outputScale = outputH / finalViewportH;
            
        // scale, clamp and floor values
        finalImageW = Math.floor(finalImageW * outputScale);
        finalImageH = Math.floor(finalImageH * outputScale);
        finalCropX = Math.max(0, Math.round(finalCropX * outputScale));
        finalCropY = Math.max(0, Math.round(finalCropY * outputScale));
        finalViewportW = Math.min(finalImageW, Math.round(finalViewportW * outputScale));
        finalViewportH = Math.min(finalImageH, Math.round(finalViewportH * outputScale));

        var url_str = "JavaScript:cropImage(" + [finalCropX, finalCropY, finalViewportW, finalViewportH, finalImageW, finalImageH, finalImageR] + ")";
        log("url_str: "+url_str);
        
        // we are inside debug mode, so do not use getURL
        if (System.capabilities.playerType == "External")
            return;
        
        getURL(url_str);
	}
	
    private function loadChanges()
    {
        // here the image is loaded, scaled and rotated properly, now transform the passed dimensions to match the image 

        centerImage();

        // use a FlashvarSetup Object to validate and init the default values of the flashvars
        var flashvarSetup = new FlashvarSetup(imageAttitude);
        currentPreset = flashvarSetup.getSelectedPreset();

        viewport_mc._x = imageAttitude.x + FlashvarManager.get("crop_x");
        viewport_mc._y = imageAttitude.y + FlashvarManager.get("crop_y");
        viewport_mc.setSize(FlashvarManager.get("crop_w"), FlashvarManager.get("crop_h"));

        updateFader();

        _level0.dropdown_mc._visible = true;
        controller_mc._visible = true;
        viewport_mc._visible = true;
        animAlphaOut.run(0);
        animAlphaIn.run(100);        

        controller_mc.init(currentPreset);
        
        changesLoaded = true;
    }
    
    // image dragging -----------------------------------------------------------------    
	
    function startDragImage()
    {
        viewportStartPoint = new Point(viewport_mc._x, viewport_mc._y);
        dragCursorStart = new Point(_xmouse, _ymouse);
        dragImageStart = new Point(imageAttitude.x, imageAttitude.y);

        onEnterFrame = dragImage;
        
        dragImage();
        Mouse.hide();
        _level0.imagetool_mc.mousepointer_mc.pointer_drag_mc._visible = true;
    }
    
    function stopDragImage(ei:EventInfo)
    {        
        onEnterFrame = onEnterFrameUpdateViewport;

        //if (!isWithinViewport(_xmouse, _ymouse))
        //{
            _level0.imagetool_mc.mousepointer_mc.pointer_drag_mc._visible = false;
            Mouse.show();
        //}

        saveChanges();
    }
    
    function dragImage()
    {
        _level0.imagetool_mc.mousepointer_mc.pointer_drag_mc._x = _level0._xmouse;
        _level0.imagetool_mc.mousepointer_mc.pointer_drag_mc._y = _level0._ymouse;

        var dX = _xmouse - dragCursorStart.x;
        var dY = _ymouse - dragCursorStart.y;
        var nextX = dragImageStart.x + dX;
        var nextY = dragImageStart.y + dY;
        
        if (imageAttitude.w >= canvas_mc._width)
        {
            if (nextX >= canvas_mc._x)
            {
                nextX = canvas_mc._x;
                dX = nextX - dragImageStart.x;
            }
                
            if (nextX + imageAttitude.w < canvas_mc._x + canvas_mc._width)
            {
                nextX = canvas_mc._x + canvas_mc._width - imageAttitude.w;
                dX = nextX - dragImageStart.x;
            }

            imageAttitude.x = nextX;
            viewport_mc._x = viewportStartPoint.x + dX;
        }
        
        if (imageAttitude.h >= canvas_mc._height)
        {
            if (nextY >= canvas_mc._y)
            {
                nextY = canvas_mc._y;
                dY = nextY - dragImageStart.y;
            }
                
            if (nextY + imageAttitude.h < canvas_mc._y + canvas_mc._height)
            {
                nextY = canvas_mc._y + canvas_mc._height - imageAttitude.h;
                dY = nextY - dragImageStart.y;
            }

            imageAttitude.y = nextY;
            viewport_mc._y = viewportStartPoint.y + dY;
        }
    }
    
    // image positioning / scaling -----------------------------------------------------------------    
	
    private function centerImage()
    {
        var deltaX = viewport_mc._x - imageAttitude.x;
        var deltaY = viewport_mc._y - imageAttitude.y;
        
        imageAttitude.x = canvas_mc._x + (canvas_mc._width - imageAttitude.w) / 2;
        imageAttitude.y = canvas_mc._y + (canvas_mc._height - imageAttitude.h) / 2;

        //viewport_mc._x = imageAttitude.x + deltaX;
        //viewport_mc._y = imageAttitude.y + deltaY;
        //updateFader();
    }
    
    private function resetImage()
    {
        imageAttitude.w = imageAttitude.initialWidth;
        imageAttitude.h = imageAttitude.initialHeight;
        centerImage();
        
        var ei:EventInfo = new EventInfo(this, "onFitImage");
        broadcastEvent(ei);
    }
    
    // important: this function doesn't operate on the imageAttitude since we first need
    // to setup the dimensions based on the stage size
    private function fitImageToStage()
    {
        var canvasRatio = canvas_mc._width / canvas_mc._height;
        var imageRatio = imageAttitude.originalWidth / imageAttitude.originalHeight;
        var dW = (canvas_mc._width - imageAttitude.originalWidth);
        var dH = (canvas_mc._height - imageAttitude.originalHeight);

        if (FlashvarManager.get("rotation") == 90 || FlashvarManager.get("rotation") == 270)
        {
            imageRatio = imageAttitude.originalHeight / imageAttitude.originalWidth;
            dW = (canvas_mc._width - imageAttitude.originalHeight);
            dH = (canvas_mc._height - imageAttitude.originalWidth);
        }

        // TODO - why dH < 0 ????
        var minLen = 0;
        var maxLen = 0;
        if (dH < 0)
        {
            minLen = (-(dW / dH) <= -canvasRatio) ? (canvas_mc._width) : (canvas_mc._height * imageRatio);
            maxLen = (-(dW / dH) >= -canvasRatio) ? (canvas_mc._height) : (canvas_mc._width / imageRatio);
        }
        else
        {
            minLen = ((dW / dH) <= canvasRatio) ? (canvas_mc._width) : (canvas_mc._height * imageRatio);
            maxLen = ((dW / dH) >= canvasRatio) ? (canvas_mc._height) : (canvas_mc._width / imageRatio);
        }

        if (FlashvarManager.get("rotation") == 90 || FlashvarManager.get("rotation") == 270)
            editable_image_mc.setSize(maxLen, minLen);
        else
            editable_image_mc.setSize(minLen, maxLen);
    }
    


    // viewport handling -----------------------------------------------------------------    	
    
    function onEnterFrameUpdateViewport()
    {
        if (isElementDragging)
        {
            if (viewport_mc.getLocked() || Key.isDown(Key.SHIFT))
                scaleViewportByRatio(currentDragElement, _xmouse, _ymouse)
            else
                scaleViewportByDragElement(currentDragElement, _xmouse, _ymouse);
        }
        
        if (isViewportDragging || isElementDragging)
            updateFader();
    }
    
    private function scaleViewportByDragElement(dragElement:String, cursorX:Number, cursorY:Number)
    {
        var lines = dragElement.split("");
        for (var i = 0; i < lines.length; i++)
        {
            var rect = getElementExtents(lines[i], cursorX, cursorY)
                
            viewport_mc._x = rect.x;
            viewport_mc._y = rect.y;
            viewport_mc.setWidth(rect.width);
            viewport_mc.setHeight(rect.height);
        }
    }
    
    private function scaleViewportByRatio(dragElement:String, cursorX:Number, cursorY:Number)
    {
        var resultX = cursorX;
        var resultY = cursorY;
        
        switch(dragElement)
        {
            case "LT":
                var startX = viewportStartPoint.x + viewportStartSize.x;
                var startY = viewportStartPoint.y + viewportStartSize.y;
                var offsetX = startX - cursorX;
                var offsetY = startY - cursorY;
                var offset = (viewportFixedRatio >= 1) ? Math.max(offsetX, offsetY) : Math.min(offsetX, offsetY);
                resultX = startX - offset;
                resultY = startY - offset / viewportFixedRatio;
                
                // clamp to window
                if (resultX <= imageAttitude.x)
                {
                    resultX = imageAttitude.x;
                    resultY = startY + (resultX - startX) / viewportFixedRatio;
                }
                
                if (resultY <= imageAttitude.y)
                {
                    resultY = imageAttitude.y;
                    resultX = startX + (resultY - startY) * viewportFixedRatio;
                }
                
                // clamp to min size if given                
                if (viewportMinSize && (viewportStartPoint.x + viewportStartSize.x - resultX < viewportMinSize.x || viewportStartPoint.y + viewportStartSize.y - resultY < viewportMinSize.y))
                {
                    resultX = viewportStartPoint.x + viewportStartSize.x - viewportMinSize.x;
                    resultY = viewportStartPoint.y + viewportStartSize.y - viewportMinSize.y;
                }
                
                // clamp to max size if given
                if (viewportMaxSize && (viewportStartPoint.x + viewportStartSize.x - resultX > viewportMaxSize.x || viewportStartPoint.y + viewportStartSize.y - resultY > viewportMaxSize.y))
                {
                    resultX = viewportStartPoint.x + viewportStartSize.x - viewportMaxSize.x;
                    resultY = viewportStartPoint.y + viewportStartSize.y - viewportMaxSize.y;
                }
                
                break;

            case "RT":
                var startX = viewportStartPoint.x;
                var startY = viewportStartPoint.y + viewportStartSize.y;
                var offsetX = cursorX - startX;
                var offsetY = startY - cursorY;
                var offset = (viewportFixedRatio >= 1) ? Math.max(offsetX, offsetY) : Math.min(offsetX, offsetY);
                resultX = startX + offset;
                resultY = startY - offset / viewportFixedRatio;
                
                // clamp to window
                if (resultX >= imageAttitude.x + imageAttitude.w)
                {
                    resultX = imageAttitude.x + imageAttitude.w;
                    resultY = startY - (imageAttitude.x + imageAttitude.w - startX) / viewportFixedRatio;
                }
                
                if (resultY <= imageAttitude.y)
                {
                    resultY = imageAttitude.y;
                    resultX = startX - (resultY - startY) * viewportFixedRatio;
                }
                
                // clamp to min size if given
                if (viewportMinSize && (resultX - viewportStartPoint.x < viewportMinSize.x || viewportStartPoint.y + viewportStartSize.y - resultY < viewportMinSize.y))
                {
                    resultX = viewportStartPoint.x + viewportMinSize.x;
                    resultY = viewportStartPoint.y + viewportStartSize.y - viewportMinSize.y;
                }
                
                // clamp to max size if given
                if (viewportMaxSize && (viewportStartPoint.x + viewportStartSize.x - resultX > viewportMaxSize.x || viewportStartPoint.y + viewportStartSize.y - resultY > viewportMaxSize.y))
                {
                    resultX = viewportStartPoint.x + viewportMaxSize.x;
                    resultY = viewportStartPoint.y + viewportStartSize.y - viewportMaxSize.y;
                }
                
                break;

            case "LB":
                var startX = viewportStartPoint.x + viewportStartSize.x;
                var startY = viewportStartPoint.y;
                var offsetX = startX - cursorX;
                var offsetY = cursorY - startY;
                var offset = (viewportFixedRatio >= 1) ? Math.max(offsetX, offsetY) : Math.min(offsetX, offsetY);
                resultX = startX - offset;
                resultY = startY + offset / viewportFixedRatio;

                // clamp to window
                if (resultX <= imageAttitude.x)
                {
                    resultX = imageAttitude.x;
                    resultY = startY - (resultX - startX) / viewportFixedRatio;
                }
                
                if (resultY >= imageAttitude.y + imageAttitude.h)
                {
                    resultY = imageAttitude.y + imageAttitude.h;
                    resultX = startX - (imageAttitude.y + imageAttitude.h - startY) * viewportFixedRatio;
                }
                
                // clamp to min size if given
                if (viewportMinSize && (viewportStartPoint.x + viewportStartSize.x - resultX < viewportMinSize.x || resultY - viewportStartPoint.y < viewportMinSize.y))
                {
                    resultX = viewportStartPoint.x + viewportStartSize.x - viewportMinSize.x;
                    resultY = viewportStartPoint.y + viewportMinSize.y;
                }
                
                // clamp to max size if given
                if (viewportMaxSize && (viewportStartPoint.x + viewportStartSize.x - resultX > viewportMaxSize.x || resultY - viewportStartPoint.y > viewportMaxSize.y))
                {
                    resultX = viewportStartPoint.x + viewportStartSize.x - viewportMaxSize.x;
                    resultY = viewportStartPoint.y + viewportMaxSize.y;
                }
                
                break;

            case "RB":
                var startX = viewportStartPoint.x;
                var startY = viewportStartPoint.y;
                var offsetX = cursorX - startX;
                var offsetY = cursorY - startY;
                var offset = (viewportFixedRatio >= 1) ? Math.max(offsetX, offsetY) : Math.min(offsetX, offsetY);
                resultX = viewportStartPoint.x + offset;
                resultY = viewportStartPoint.y + offset / viewportFixedRatio;

                // clamp to window
                if (resultX >= imageAttitude.x + imageAttitude.w)
                {
                    resultX = imageAttitude.x + imageAttitude.w;
                    resultY = startY + (imageAttitude.x + imageAttitude.w - startX) / viewportFixedRatio;
                }
                
                if (resultY >= imageAttitude.y + imageAttitude.h)
                {
                    resultY = imageAttitude.y + imageAttitude.h;
                    resultX = startX + (imageAttitude.y + imageAttitude.h - startY) * viewportFixedRatio;
                }
                
                // clamp to min size if given
                if (viewportMinSize && (resultX - viewportStartPoint.x < viewportMinSize.x || resultY - viewportStartPoint.y < viewportMinSize.y))
                {
                    resultX = viewportStartPoint.x + viewportMinSize.x;
                    resultY = viewportStartPoint.y + viewportMinSize.y;
                }
                
                // clamp to max size if given
                if (viewportMaxSize && (resultX - viewportStartPoint.x > viewportMaxSize.x || resultY - viewportStartPoint.y > viewportMaxSize.y))
                {
                    resultX = viewportStartPoint.x + viewportMaxSize.x;
                    resultY = viewportStartPoint.y + viewportMaxSize.y;
                }
                
                break;
        }
        
        scaleViewportByDragElement(dragElement, resultX, resultY);
    }
    
    private function getElementExtents(dragElement:String, cursorX:Number, cursorY:Number):Rectangle
    {
        return getLineExtents(dragElement, cursorX, cursorY);
    }
    
    private function getLineExtents(dragElement:String, cursorX:Number, cursorY:Number):Rectangle
    {
        switch(dragElement)
        {
            case "L":
                var dw = cursorX - dragStartPoint.x;
                var rightPosX = viewportStartPoint.x + viewportStartSize.x;
                var nextWidth = viewportStartSize.x - dw;

                if (rightPosX - nextWidth < imageAttitude.x)
                    return new Rectangle(imageAttitude.x, viewport_mc._y, rightPosX - imageAttitude.x, viewport_mc._height)
                
                if (rightPosX - nextWidth > viewportStartPoint.x + viewportStartSize.x - MIN_VIEWPORT_SIZE)
                    return new Rectangle(viewportStartPoint.x + viewportStartSize.x - MIN_VIEWPORT_SIZE, viewport_mc._y, MIN_VIEWPORT_SIZE, viewport_mc._height);

                return new Rectangle(viewportStartPoint.x + dw, viewport_mc._y, viewportStartSize.x - dw, viewport_mc._height);

            case "T":
                var dh = cursorY - dragStartPoint.y;
                var bottomPosY = viewportStartPoint.y + viewportStartSize.y;
                var nextHeight = viewportStartSize.y - dh;

                if (bottomPosY - nextHeight < imageAttitude.y)
                    return new Rectangle(viewport_mc._x, imageAttitude.y, viewport_mc._width, bottomPosY - imageAttitude.y);

                if (bottomPosY - nextHeight > viewportStartPoint.y + viewportStartSize.y - MIN_VIEWPORT_SIZE)
                    return new Rectangle(viewport_mc._x, viewportStartPoint.y + viewportStartSize.y - MIN_VIEWPORT_SIZE, viewport_mc._width, MIN_VIEWPORT_SIZE);

                return new Rectangle(viewport_mc._x, viewportStartPoint.y + dh, viewport_mc._width, viewportStartSize.y - dh);

            case "R":
                var dw = cursorX - dragStartPoint.x;
                var w = viewportStartSize.x + dw;

                if (viewportStartPoint.x + w > imageAttitude.x + imageAttitude.w)
                    return new Rectangle(viewport_mc._x, viewport_mc._y, imageAttitude.x + imageAttitude.w - viewportStartPoint.x, viewport_mc._height);

                if (w < MIN_VIEWPORT_SIZE)
                    return new Rectangle(viewport_mc._x, viewport_mc._y, MIN_VIEWPORT_SIZE, viewport_mc._height);

                return new Rectangle(viewport_mc._x, viewport_mc._y, viewportStartSize.x + dw, viewport_mc._height);

            case "B":
                var dh = cursorY - dragStartPoint.y;
                var h = viewportStartSize.y + dh;

                if (viewportStartPoint.y + h > imageAttitude.y + imageAttitude.h)
                    return new Rectangle(viewport_mc._x, viewport_mc._y, viewport_mc._width, imageAttitude.y + imageAttitude.h - viewportStartPoint.y);

                if (h < MIN_VIEWPORT_SIZE)
                    return new Rectangle(viewport_mc._x, viewport_mc._y, viewport_mc._width, MIN_VIEWPORT_SIZE);

                return new Rectangle(viewport_mc._x, viewport_mc._y, viewport_mc._width, viewportStartSize.y + dh);
        }
        
        return null;
    }
        
    private function moveViewportBy(x:Number, y:Number)
    {
        if (viewport_mc._x + x < imageAttitude.x)
            viewport_mc._x = imageAttitude.x;
        else if (viewport_mc._x + x > imageAttitude.x + imageAttitude.w - viewport_mc._width)
            viewport_mc._x = imageAttitude.x + imageAttitude.w - viewport_mc._width;
        else
            viewport_mc._x += x;
            
        if (viewport_mc._y + y < imageAttitude.y)
            viewport_mc._y = imageAttitude.y;
        else if (viewport_mc._y + y > imageAttitude.y + imageAttitude.h - viewport_mc._height)
            viewport_mc._y = imageAttitude.y + imageAttitude.h - viewport_mc._height;
        else
            viewport_mc._y += y;
        
        updateFader();
        saveChanges();
    }
    
    private function resetViewport()
    {
        //if (!changesLoaded)
        //    return;
        
        var viewport_reset = currentPreset.resetCoords;
        viewport_mc.setSize(viewport_reset.x, viewport_reset.y);
        viewport_mc._x = imageAttitude.x + (imageAttitude.w - viewport_mc._width) / 2;
        viewport_mc._y = imageAttitude.y + (imageAttitude.h - viewport_mc._height) / 2;
        log("RESETTING: " + currentPreset.name + " " + viewport_mc._width + " " + viewport_mc._height)
    }

    // menu event listeners --------------------------------------------------------------
    
    function onRotateLeftRelease(ei:EventInfo)
    {
        viewport_mc._visible = false;
        editable_image_mc.setFaderVisible(false);
        resetImage();
        imageAttitude.rotateLeft();
    }
    
    function onRotateRightRelease(ei:EventInfo)
    {
        viewport_mc._visible = false;
        editable_image_mc.setFaderVisible(false);
        resetImage();
        imageAttitude.rotateRight();
    }

    var viewportImageRatio;
    var imageStartSize;
    var imageStartCenter;
    var imageStartPoint;
    var viewportStartCenter;

    function onSliderPress(ei:EventInfo)
    {
        var viewportDeltaX = viewport_mc._x - imageAttitude.x;
        var viewportDeltaY = viewport_mc._y - imageAttitude.y;
        centerImage();
        viewport_mc._x = imageAttitude.x + viewportDeltaX;
        viewport_mc._y = imageAttitude.y + viewportDeltaY;

        imageMinMaxDelta = new Point(imageAttitude.originalWidth - imageAttitude.initialWidth, imageAttitude.originalHeight - imageAttitude.initialHeight);

        viewportImageRatio = new Point(viewport_mc._width / imageAttitude.w, viewport_mc._height / imageAttitude.h);
        imageStartPoint = new Point(imageAttitude.x, imageAttitude.y);
        imageStartSize = new Point(imageAttitude.w, imageAttitude.h);
        viewportStartPoint = new Point(viewport_mc._x, viewport_mc._y);
        viewportStartSize = new Point(viewport_mc._width, viewport_mc._height);

        // these are in image coordinates
        imageStartCenter = new Point(imageAttitude.w / 2, imageAttitude.h / 2);
        viewportStartCenter = new Point(viewport_mc._x - imageAttitude.x + viewport_mc._width / 2, viewport_mc._y - imageAttitude.y + viewport_mc._height / 2);

        mapViewportToImage();
    }
    
    function onSliderChange(ei:EventInfo)
    {
        currentPercent = ei.getInfo("percent");
        
        var imageDeltaX = imageMinMaxDelta.x * currentPercent;
        var imageDeltaY = imageMinMaxDelta.y * currentPercent;
        
        imageAttitude.w = imageAttitude.initialWidth + imageDeltaX;
        imageAttitude.h = imageAttitude.initialHeight + imageDeltaY;
        
        centerImage();

        mapViewportToImage();
        
        editable_image_mc.setFaderVisible(currentPercent == 0);
        if (currentPercent == 0)
            updateFader();

        // TODO - remove this and scale viewport when zooming
/*
        viewport_mc._visible = percent == 0;
        editable_image_mc.setFaderVisible(percent == 0);
        if (percent == 0)
        {
            resetViewport();
            updateFader();
            saveChanges();
        }
*/
        // !TODO
    }
    
    function onViewportRatioChange(ei:EventInfo)
    {
        currentPreset = ei.getInfo("preset");
        var isLocked = !!currentPreset.ratio;

        viewport_mc.setLocked(isLocked);
        viewportOutputSize = null;
        viewportMinSize = null;
        viewportMaxSize = null;
        viewportFixedRatio = 0;

        if (!isLocked)
        {
            viewportFixedRatio = 1;
        }
        else if (currentPreset.ratio)
        {
            viewportFixedRatio = currentPreset.ratio;
        }
        else 
        {
            if (currentPreset.output_w && currentPreset.output_h)
            {
                viewportFixedRatio = parseInt(currentPreset.output_w) / parseInt(currentPreset.output_h);
                viewportOutputSize = new Point(parseInt(currentPreset.output_w), parseInt(currentPreset.output_h));
            }
            
            if (currentPreset.min_w && currentPreset.min_h)
            {
                if (!viewportFixedRatio)
                    viewportFixedRatio = parseInt(currentPreset.min_w) / parseInt(currentPreset.min_h);
                viewportMinSize = new Point(parseInt(currentPreset.min_w), parseInt(currentPreset.min_h));
            }
            
            if (currentPreset.max_w && currentPreset.max_h)
            {
                if (!viewportFixedRatio)
                    viewportFixedRatio = parseInt(currentPreset.max_w) / parseInt(currentPreset.max_h);
                viewportMaxSize = new Point(parseInt(currentPreset.max_w), parseInt(currentPreset.max_h));
            }
            
            if (!viewportFixedRatio)
                viewportFixedRatio = 1;
        }

        if (changesLoaded)
            resetViewport();

        updateFader();
        saveChanges();
    }
    
    // event listeners --------------------------------------------------------------
    
    function onImageLoaded(ei:EventInfo)
    {
        // call resize once to setup everything up properly
        onResize();

        imageAttitude = new EditableImageAttitude(editable_image_mc);
        imageAttitude.addListener(this);        
        imageAttitude.setOriginalSize(editable_image_mc._width, editable_image_mc._height);
        
        // first make the image fit into the canvas
        fitImageToStage();
        centerImage();

        // then init the attitude object so we get the registration point right
        imageAttitude.setTarget(editable_image_mc);
        
        // if the image is rotated, do this first and then load changes
        if (FlashvarManager.get("rotation") > 0)
            imageAttitude.rotate(FlashvarManager.get("rotation"));
        else
            loadChanges();
    }
    
    function onImageRotated(ei:EventInfo)
    {
        // if changes were not loaded yet, we had to rotate the image first - load changes now
        if (!changesLoaded)
        {
            loadChanges();
            return;
        }
        
        editable_image_mc.setFaderVisible(true)
        viewport_mc._visible = true;
        resetViewport();
        updateFader();
        centerImage();
        saveChanges();
    }

    function onViewportPress(ei:EventInfo)
    {
        var areaX = imageAttitude.x;
        var areaY = imageAttitude.y;
        var areaW = imageAttitude.x + imageAttitude.w - viewport_mc._width;
        var areaH = imageAttitude.y + imageAttitude.h - viewport_mc._height;
        viewport_mc.startDrag(false, areaX, areaY, areaW, areaH);
        isViewportDragging = true;
    }
    
    function onViewportRelease(ei:EventInfo)
    {
        viewport_mc.stopDrag();
        updateFader();
        isViewportDragging = false;
        saveChanges();
    }

    function onDragElementPress(ei:EventInfo)
    {
        currentDragElement = ei.getInfo("type");
        viewportStartPoint = new Point(viewport_mc._x, viewport_mc._y);
        viewportStartSize = new Point(viewport_mc._width, viewport_mc._height);
        dragStartPoint = new Point(ei.getInfo("dragStartX"), ei.getInfo("dragStartY"));
        isElementDragging = true;
    }
    
    function onDragElementRelease(ei:EventInfo)
    {
        isElementDragging = false;
        saveChanges();
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
        }        
    }
    
    function onMouseDown()
    {
        if (!isOverImage(_xmouse, _ymouse))
            return;
        
        if (imageAttitude.w <= canvas_mc._width && imageAttitude.h <= canvas_mc._height)
            return;

        startDragImage();
    }
    
    function onMouseUp()
    {
        stopDragImage();
    }
    
    function onImageRollOver(ei:EventInfo)
    {
        /*
        if (imageCanBeDragged())
        {
            onEnterFrameUpdateDragCursor();
            _level0.imagetool_mc.mousepointer_mc.pointer_drag_mc._visible = true;
            Mouse.hide();
            onEnterFrame = onEnterFrameUpdateDragCursor;
        }
        else
        {
            _level0.imagetool_mc.mousepointer_mc.pointer_drag_mc._visible = false;
            Mouse.show();
            onEnterFrame = onEnterFrameUpdateViewport;
        }
        */
    }
    
    function onEnterFrameUpdateDragCursor()
    {
        _level0.imagetool_mc.mousepointer_mc.pointer_drag_mc._x = _level0._xmouse;
        _level0.imagetool_mc.mousepointer_mc.pointer_drag_mc._y = _level0._ymouse;
    }
    
    function onImageRollOut(ei:EventInfo)
    {
        /*
        _level0.imagetool_mc.mousepointer_mc.pointer_drag_mc._visible = false;
        Mouse.show();
        onEnterFrame = onEnterFrameUpdateViewport;
        */
    }
    
    public function onResize()
    {
        var w = Stage.width - 2 * PADDING;
        var h = Stage.height - 2 * PADDING;
        
        var controllerHeight = 45;
        controller_mc.onParentResize(w, controllerHeight);
        controller_mc._x = PADDING;
        controller_mc._y = Stage.height - PADDING - controller_mc._height;
        
        var canvasHeight = controller_mc._y - PADDING - PADDING;
        canvas_mc.onParentResize(w, canvasHeight);
        canvas_mc._x = PADDING;
        canvas_mc._y = PADDING;
        
        var viewportDeltaX = viewport_mc._x - imageAttitude.x;
        var viewportDeltaY = viewport_mc._y - imageAttitude.y;
        centerImage();
        viewport_mc._x = imageAttitude.x + viewportDeltaX;
        viewport_mc._y = imageAttitude.y + viewportDeltaY;
        
        if (changesLoaded)
        {
            updateFader();
            saveChanges();
        }
    }
    
    private function updateFader()
    {
        var x = 0;
        var y = 0;
        var w = 0;
        var h = 0;
        
        switch(imageAttitude.r)
        {
            case 0:
                x = viewport_mc._x - imageAttitude.x;
                y = viewport_mc._y - imageAttitude.y;
                w = Math.min(imageAttitude.w, Math.round(viewport_mc._width))
                h = Math.min(imageAttitude.h, Math.round(viewport_mc._height));
                break;
                
            case 90:
                x = imageAttitude.y + imageAttitude.h - (viewport_mc._y + viewport_mc._height);
                y = viewport_mc._x - imageAttitude.x;
                w = Math.min(imageAttitude.h, Math.round(viewport_mc._height))
                h = Math.min(imageAttitude.w, Math.round(viewport_mc._width));
                break;

            case 180:
                x = imageAttitude.w - viewport_mc._x + imageAttitude.x - viewport_mc._width;
                y = imageAttitude.h - viewport_mc._y + imageAttitude.y - viewport_mc._height;
                w = Math.min(imageAttitude.w, Math.round(viewport_mc._width))
                h = Math.min(imageAttitude.h, Math.round(viewport_mc._height));
                break;

            case 270:
                x = viewport_mc._y - imageAttitude.y;
                y = imageAttitude.w - viewport_mc._x + imageAttitude.x - viewport_mc._width;
                w = Math.min(imageAttitude.h, Math.round(viewport_mc._height))
                h = Math.min(imageAttitude.w, Math.round(viewport_mc._width));
                break;
        }

        x = Math.max(0, Math.round(x));
        y = Math.max(0, Math.round(y));
        
        editable_image_mc.setVisibleArea(new Rectangle(x, y, w, h));
    }
    
    private function mapViewportToImage()
    {
        var imageDW = imageAttitude.w - imageStartSize.x;
        var imageDH = imageAttitude.h - imageStartSize.y;
        
        var viewportW = viewportStartSize.x + imageDW * viewportImageRatio.x;
        var viewportH = viewportStartSize.y + imageDH * viewportImageRatio.y;
        viewport_mc.setSize(viewportW, viewportH);
        
        var viewportDW = (viewportStartSize.x - viewportW) / 2;
        var viewportDH = (viewportStartSize.y - viewportH) / 2;
        
        var facX = ((viewportStartCenter.x - imageStartCenter.x) / imageStartCenter.x);
        viewport_mc._x = viewportStartPoint.x + viewportDW + facX * imageDW / 2;

        var facY = ((viewportStartCenter.y - imageStartCenter.y) / imageStartCenter.y);
        viewport_mc._y = viewportStartPoint.y + viewportDH + facY * imageDH / 2;
    }
    
    // helpers -------------------------------------------------------------------------
    
    public function isWithinCanvas(x:Number, y:Number, w:Number, h:Number)
    {
        w = (w == undefined) ? 0 : w;
        h = (h == undefined) ? 0 : h;
        return (x >= canvas_mc._x) && (x < canvas_mc._x + canvas_mc._width) &&  (y >= canvas_mc._y) && (y < canvas_mc._y + canvas_mc._height);
    }
    
    public function isWithinImage(x:Number, y:Number, w:Number, h:Number)
    {
        w = (w == undefined) ? 0 : w;
        h = (h == undefined) ? 0 : h;
        return (x >= imageAttitude.x) && (x + w < imageAttitude.x + imageAttitude.w) && (y >= imageAttitude.y) && (y + h < imageAttitude.y + imageAttitude.h);
    }
    
    public function isWithinViewport(x:Number, y:Number)
    {
        return (x >= viewport_mc._x) && (x < viewport_mc._x + viewport_mc._width) &&  (y >= viewport_mc._y) && (y < viewport_mc._y + viewport_mc._height);
    }
    
    public function isOverImage(x:Number, y:Number)
    {
        return isWithinCanvas(x, y) && isWithinImage(x, y) && !isWithinViewport(x, y);
    }
    
    public function imageCanBeDragged():Boolean
    {
        return imageAttitude.w > canvas_mc._width || imageAttitude.h > canvas_mc._height;
    }
    
    public function isOverController(x:Number, y:Number)
    {
        return (x >= controller_mc._x) && (y >= controller_mc._y) && (x < controller_mc._x + controller_mc._width) && (y < controller_mc._y + controller_mc._height);
    }
}
