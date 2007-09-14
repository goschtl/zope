/**
* z3c.reference.imagetool.baseskin.ImageTool 
* is a tool for cropping images TTW
*
* @author <viktor.sohm@lovelysystems.com>
* @author <manfred.schwendinger@lovelysystems.com>
* @author <armin.wolf@lovelysystems.com>
* @author <gerold.boehler@lovelysystems.com>
*/

import z3c.reference.imagetool.core.*;
import z3c.reference.imagetool.baseskin.*;


class z3c.reference.imagetool.baseskin.ImageTool extends Component
{
    private var PADDING:Number = 10;

    private var canvas_mc:MovieClip;
    private var editable_image_mc:MovieClip;
    private var mousepointer_mc:MovieClip;
    private var controller_mc:MovieClip;
    
    private var imageScale:Number = 100;
    private var imageRatio:Number = 1;
    private var maxImageWidth:Number = 0;
    private var maxImageHeight:Number = 0;

    private var editableImageStartX:Number = 0;
    private var editableImageStartY:Number = 0;
    private var editableImageStartWidth:Number = 1;
    private var editableImageStartHeight:Number = 1;
    private var zoomLevel:Number = 0;
    private var nextDegree:Number = 0;
    
    private var dragCursorStartX:Number = 0;
    private var dragCursorStartY:Number = 0;
    private var dragImageStartX:Number = 0;
    private var dragImageStartY:Number = 0;
    
    private var isDraggingImage:Boolean = false;

	function ImageTool()
	{
	    super();
	    
	    attachMovie("canvas_mc", "canvas_mc", getNextHighestDepth());

	    attachMovie("editable_image_mc", "editable_image_mc", getNextHighestDepth());
	    editable_image_mc.addListener(this);
	    editable_image_mc.setMask(canvas_mc.getMask());
	    
	    createEmptyMovieClip("mousepointer_mc", getNextHighestDepth());
	    mousepointer_mc.attachMovie("pointer_drag_mc", "pointer_drag_mc", mousepointer_mc.getNextHighestDepth(), {_visible: false});
	    mousepointer_mc.attachMovie("pointer_line_mc", "pointer_line_mc", mousepointer_mc.getNextHighestDepth(), {_visible: false});
	    mousepointer_mc.attachMovie("pointer_corner_mc", "pointer_corner_mc", mousepointer_mc.getNextHighestDepth(), {_visible: false});	    
	    
	    attachMovie("controller_mc", "controller_mc", getNextHighestDepth());
	    controller_mc.addListener(this);
	    
	    _visible = false;
        onEnterFrame = initAfterFirstFrame;
        Stage.addListener(this);
    }
    
    var tmp = 0;
    function initAfterFirstFrame()
    {
        editable_image_mc.loadImage(FlashvarManager.get("url"));
        onEnterFrame = null;//function() { rotateImage(tmp); tmp += 0.01;};
    }
    
	function saveChanges()
	{
        trace("\n\nsaveChanges");
        
        var url_str:String="";
        
        url_str+="JavaScript:cropImage(";
        
        //crop_x = Math.round(bounding_mc.left-image_mc.left)//Math.round((bounding_mc.left-image_mc.left) / image_mc.getZoomFactor());
        //crop_y = Math.round(bounding_mc.top-image_mc.top)//Math.round((bounding_mc.top-image_mc.top) / image_mc.getZoomFactor());
        
        
        //var rotation:Number = (Math.round(image_mc.getRotation()) % 360)*-1; //seems like pil accepts rotation in the other direction
        //rotation = rotation > 0 ? rotation : rotation + 360;
        
        //url_str += crop_x + ", ";        
        //url_str += crop_y + ", ";        
        
        //url_str += output_w + ", ";
        //url_str += output_h + ", ";
        /*
        if (rotation==90 || rotation==270)
        {
            url_str += Math.round(original_h * image_mc.getZoomFactor()) + ", ";
            url_str += Math.round(original_w * image_mc.getZoomFactor()) + ", " ;
        }
        else
        {
            url_str += Math.round(original_w * image_mc.getZoomFactor()) + ", " ;
            url_str += Math.round(original_h * image_mc.getZoomFactor()) + ", ";
        }
        */
        
        //url_str += rotation.toString() + ", ";
        //url_str += image_mc.getZoomFactor()+"";
        
        var globalTL = new flash.geom.Point();
        var cropPos = new Object();
        var cropDim = new Object();
        var imageDim = new Object();

        switch(nextDegree)
        {
            case 0:
                imageDim.x = editable_image_mc._width;
                imageDim.y = editable_image_mc._height;
                globalTL.x = canvas_mc._x + (canvas_mc._width - editable_image_mc._width) / 2;
                globalTL.y = canvas_mc._y + (canvas_mc._height - editable_image_mc._height) / 2;

                var scaleFactor = editable_image_mc._width / maxImageWidth;
                cropDim.x = editable_image_mc.getCropDimension().x;
                cropDim.y = editable_image_mc.getCropDimension().y;
                cropDim.x *= scaleFactor;
                cropDim.y *= scaleFactor;
                
                cropPos.x = editable_image_mc.getCropPosition().x;
                cropPos.y = editable_image_mc.getCropPosition().y;
                editable_image_mc.localToGlobal(cropPos);
                cropPos.x -= globalTL.x;
                cropPos.y -= globalTL.y;

                break;
                
            case 180:
                imageDim.x = editable_image_mc._width;
                imageDim.y = editable_image_mc._height;

                globalTL.x = canvas_mc._x + (canvas_mc._width - editable_image_mc._width) / 2;
                globalTL.y = canvas_mc._y + (canvas_mc._height - editable_image_mc._height) / 2;

                var scaleFactor = editable_image_mc._width / maxImageWidth;
                cropDim.x = editable_image_mc.getCropDimension().x;
                cropDim.y = editable_image_mc.getCropDimension().y;
                cropDim.x *= scaleFactor;
                cropDim.y *= scaleFactor;

                cropPos.x = editable_image_mc.getCropPosition().x + editable_image_mc.getCropDimension().x;
                cropPos.y = editable_image_mc.getCropPosition().y + editable_image_mc.getCropDimension().y;
                editable_image_mc.localToGlobal(cropPos);
                cropPos.x -= globalTL.x;
                cropPos.y -= globalTL.y;

                break;
                
            case 90:
                editable_image_mc._rotation = 0;

                imageDim.x = editable_image_mc._height;
                imageDim.y = editable_image_mc._width;

                globalTL.x = canvas_mc._y + (canvas_mc._width - editable_image_mc._height) / 2;
                globalTL.y = canvas_mc._x + (canvas_mc._height - editable_image_mc._width) / 2;

                var scaleFactor = editable_image_mc._height / maxImageHeight;
                cropDim.x = editable_image_mc.getCropDimension().y;
                cropDim.y = editable_image_mc.getCropDimension().x;
                cropDim.x *= scaleFactor;
                cropDim.y *= scaleFactor;
            
                cropPos.x = editable_image_mc.getCropPosition().y;
                cropPos.y = editable_image_mc.getCropPosition().x;
                editable_image_mc.localToGlobal(cropPos);
                cropPos.x = 2*editable_image_mc._height - cropPos.x + globalTL.x - cropDim.y;
                cropPos.y = cropPos.y - globalTL.y;

                editable_image_mc._rotation = nextDegree;

                break;
                
            case 270:
                editable_image_mc._rotation = 0;

                imageDim.x = editable_image_mc._height;
                imageDim.y = editable_image_mc._width;

                globalTL.x = canvas_mc._y + (canvas_mc._width - editable_image_mc._height) / 2;
                globalTL.y = canvas_mc._x + (canvas_mc._height - editable_image_mc._width) / 2;

                var scaleFactor = editable_image_mc._height / maxImageHeight;
                cropDim.x = editable_image_mc.getCropDimension().y;
                cropDim.y = editable_image_mc.getCropDimension().x;
                cropDim.x *= scaleFactor;
                cropDim.y *= scaleFactor;
                
                cropPos.x = editable_image_mc.getCropPosition().y;
                cropPos.y = editable_image_mc.getCropPosition().x;
                editable_image_mc.localToGlobal(cropPos);
                cropPos.x = cropPos.x - globalTL.x;
                cropPos.y = 2*editable_image_mc._width - cropPos.y + globalTL.y - cropDim.x;

                editable_image_mc._rotation = nextDegree;

                break;
        }
        
        var rotation = ((360 - nextDegree) % 360);
        
        url_str += [Math.round(cropPos.x), Math.round(cropPos.y), Math.round(cropDim.x), Math.round(cropDim.y), Math.round(imageDim.x), Math.round(imageDim.y), rotation].toString();
        url_str+=");";
        trace("url_str: "+url_str);
        
        // we are inside debug mode, so do not use getURL
        if (System.capabilities.playerType == "External")
            return;
        
        getURL(url_str);
	}
	
	function onMouseMove()
	{
	    //trace(_level0._xmouse + " " +  _level0._ymouse)
	}
	
	private function zoomImage(dir:Number)
	{
	    if (zoomLevel + dir < 0 || zoomLevel + dir > 100)
	        return;
	    
	    zoomLevel += dir;
	    
	    var newImageWidth = editableImageStartWidth * (1 + zoomLevel / 100.0);
	    var newImageHeight = editableImageStartHeight * (1 + zoomLevel / 100.0);
        var dx = editableImageStartWidth - newImageWidth;
        var dy = editableImageStartHeight - newImageHeight;
        trace(nextDegree)
        switch(nextDegree)
        {
            case 0:
                editable_image_mc._width = editableImageStartWidth * (1 + zoomLevel / 100.0);
                editable_image_mc._height = editableImageStartHeight * (1 + zoomLevel / 100.0);
                editable_image_mc._x = editableImageStartX + dx/2;
                editable_image_mc._y = editableImageStartY + dy/2;
                break;
                
            case 90:
                editable_image_mc._rotation = 0;
                editable_image_mc._width = editableImageStartWidth * (1 + zoomLevel / 100.0);
                editable_image_mc._height = editableImageStartHeight * (1 + zoomLevel / 100.0);
                editable_image_mc._rotation = nextDegree;
                editable_image_mc._x = editableImageStartX - dx/2;
                editable_image_mc._y = editableImageStartY + dy/2;
                break;
            
            case 180:
                editable_image_mc._width = editableImageStartWidth * (1 + zoomLevel / 100.0);
                editable_image_mc._height = editableImageStartHeight * (1 + zoomLevel / 100.0);
                editable_image_mc._x = editableImageStartX - dx/2;
                editable_image_mc._y = editableImageStartY - dy/2;
                break;

            case 270:
                editable_image_mc._rotation = 0;
                editable_image_mc._width = editableImageStartWidth * (1 + zoomLevel / 100.0);
                editable_image_mc._height = editableImageStartHeight * (1 + zoomLevel / 100.0);
                editable_image_mc._rotation = nextDegree;
                editable_image_mc._x = editableImageStartX + dx/2;
                editable_image_mc._y = editableImageStartY - dy/2;
                break;
        }
	}

    // event listeners --------------------------------------------------------------
    
    function onImageLoaded(ei:EventInfo)
    {
        // save the original image dimensions
        maxImageWidth = editable_image_mc._width;
        maxImageHeight = editable_image_mc._height;
        imageRatio = maxImageWidth / maxImageHeight;
        
        // call resize once to setup everything up properly
        onResize();

        // save the initial position and dimension of the image
        editableImageStartX = editable_image_mc._x;
        editableImageStartY = editable_image_mc._y;
        editableImageStartWidth = editable_image_mc._width;
        editableImageStartHeight = editable_image_mc._height;

        _visible = true;
    }

    function onImagePress(ei:EventInfo)
    {
        if (zoomLevel == 0)
            return;
        
        if (_xmouse < canvas_mc._x || _xmouse > canvas_mc._x + canvas_mc._width ||
            _ymouse < canvas_mc._y || _ymouse > canvas_mc._y + canvas_mc._height)
            return;
        
        dragCursorStartX = _level0._xmouse;
        dragCursorStartY = _level0._ymouse;
        dragImageStartX = editable_image_mc._x;
        dragImageStartY = editable_image_mc._y;

        onEnterFrame = dragImage;
        Mouse.hide();
        _level0.imagetool_mc.mousepointer_mc.pointer_drag_mc._visible = true;
    }
    
    function onImageRelease(ei:EventInfo)
    {
        if (zoomLevel == 0)
            return;
        
        onEnterFrame = null;
        Mouse.show();
        _level0.imagetool_mc.mousepointer_mc.pointer_drag_mc._visible = false;
    }
    
    // controller event listeners --------------------------------------------------------------

    // menu event listeners --------------------------------------------------------------
    
    function onRotateLeftRelease(ei:EventInfo)
    {
        nextDegree = (editable_image_mc._rotation - 90) % 360;
        nextDegree = (nextDegree < 0) ? ( nextDegree + 360) : nextDegree;        
        centerImage();
        editable_image_mc._rotation = nextDegree;
    }
    
    function onRotateRightRelease(ei:EventInfo)
    {
        nextDegree = (editable_image_mc._rotation + 90) % 360;
        centerImage();
        editable_image_mc._rotation = nextDegree;
    }
    
    function onZoomInPress(ei:EventInfo)
    {
        onEnterFrame = function() { zoomImage(1, 2); }
    }
    
    function onZoomInRelease(ei:EventInfo)
    {
        onEnterFrame = null;
    }
    
    function onZoomOutPress(ei:EventInfo)
    {
        onEnterFrame = function() { zoomImage(-1, 2); }
    }
    
    function onZoomOutRelease(ei:EventInfo)
    {
        onEnterFrame = null;
    }
    
    function onAbortRelease(ei:EventInfo)
    {

    }
    
    function onAcceptRelease(ei:EventInfo)
    {
        saveChanges();
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
        
        centerImage();
    }
    
    // helpers ----------------------------------------------------------------------------
    
    function dragImage()
    {
        _level0.imagetool_mc.mousepointer_mc.pointer_drag_mc._x = _level0._xmouse;
        _level0.imagetool_mc.mousepointer_mc.pointer_drag_mc._y = _level0._ymouse;
        
        var nextX = dragImageStartX + _xmouse - dragCursorStartX;
        var nextY = dragImageStartY + _ymouse - dragCursorStartY;
        if (nextX <= canvas_mc._x && nextX + editable_image_mc._width >= canvas_mc._x + canvas_mc._width)
            editable_image_mc._x = nextX;

        if (nextY <= canvas_mc._y && nextY + editable_image_mc._height >= canvas_mc._y + canvas_mc._height)
            editable_image_mc._y = nextY;
    }
    
    private function centerImage()
    {
        fitImage();
        
        var dx = canvas_mc._width - editable_image_mc._width;
        var dy = canvas_mc._height - editable_image_mc._height;

        switch(nextDegree)
        {
            case 0:
                editable_image_mc._x = canvas_mc._x + dx/2;
                editable_image_mc._y = canvas_mc._y + dy/2;
                break;
                
            case 90:
                editable_image_mc._x = canvas_mc._x + editable_image_mc._width + dx/2;
                editable_image_mc._y = canvas_mc._y + dy/2;
                break;
            
            case 180:
                editable_image_mc._x = canvas_mc._x + editable_image_mc._width + dx/2;
                editable_image_mc._y = canvas_mc._y + editable_image_mc._height + dy/2;
                break;
                
            case 270:
                editable_image_mc._x = canvas_mc._x + dx/2;
                editable_image_mc._y = canvas_mc._y + editable_image_mc._height + dy/2;
                break;
        }

        editableImageStartX = editable_image_mc._x;
        editableImageStartY = editable_image_mc._y;
    }
    
    private function fitImage()
    {
        editable_image_mc._rotation = 0;

        var dW = editable_image_mc._width - canvas_mc._width;
        var dH = editable_image_mc._height - canvas_mc._height;

        switch(nextDegree)
        {
            case 0:
            case 180:
                if (dW < dH)
                {
                    editable_image_mc._width = canvas_mc._height * imageRatio;
                    editable_image_mc._height = canvas_mc._height;
                }
                else
                {
                    editable_image_mc._width = canvas_mc._width;
                    editable_image_mc._height = canvas_mc._width / imageRatio;
                }
                break;
                
            case 90:
            case 270:            
                if (dW < dH)
                {
                    editable_image_mc._width = canvas_mc._height;
                    editable_image_mc._height = canvas_mc._height / imageRatio;
                }
                else
                {
                    editable_image_mc._width = canvas_mc._width * imageRatio;
                    editable_image_mc._height = canvas_mc._width;
                }
                break;
        }
        
        editableImageStartWidth = editable_image_mc._width;
        editableImageStartHeight = editable_image_mc._height;
        editable_image_mc._rotation = nextDegree;
        zoomLevel = 0;
    }    
}
