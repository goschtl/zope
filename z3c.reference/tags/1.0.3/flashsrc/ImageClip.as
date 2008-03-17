 /**
* Class ImageClip
* This Class contains the image and functions to directly manipulate (zoom or rotate) the image
*
* @author viktor.sohm@lovelysystems.com
* @author manfred.schwendinger@lovelysystems.com
* @author armin.wolf@lovelysystems.com
*/

class ImageClip extends MovieClip{
	
    private var zoomer_mc:MovieClip;
    public var tool:ImageTool;
    private var mc_loader:MovieClipLoader;
    private var mode:String;
	private var mousePressed:Boolean;
    
    public function ImageClip(){
        mc_loader = new MovieClipLoader();
        mode = "crop";
        this.createEmptyMovieClip("zoomer_mc", 1);
        this.zoomer_mc.createEmptyMovieClip("rotator_mc", 1);
        
        var shadow=new flash.filters.DropShadowFilter(3);
        filters=[shadow];
        
        
    }
    
    public function get left():Number {return _x};
    public function get top():Number {return _y};
    public function get right():Number {return _x+getImageWidth()};
    public function get bottom():Number {return _y+getImageHeight()};
    
    public function setMode(m:String):Void{
        if (m==mode) return; // no change
        mode = m;
    }

    public function getMcLoader():MovieClipLoader{
        return mc_loader;
    }
    
    /**
	* Loads the image into the ImageClip Class
	* @param needs the image path as parameter as String
	*/
	function loadImage(path:String):Void{
        mc_loader.loadClip(path, this.zoomer_mc.rotator_mc);
        mc_loader.addListener(this);
	}
    
    public function getOriginalWidth():Number {
        //return values depending on rotation
        //return Math.abs(getRotation())==90 ? original_height : original_width;
    
        return getImageWidth()/getZoomFactor();
    }
    public function getOriginalHeight():Number {
        return getImageHeight()/getZoomFactor();
        //return Math.abs(getRotation())==90 ? original_width : original_height;
    }
    
    
    /**
        @return the current zoom factor.
        e.g. 2 if the image is twice as big as the original.
    */
    public function getZoomFactor():Number{
        return this.zoomer_mc._xscale/100;
    }
    
    public function getRotation():Number{
        return this.zoomer_mc.rotator_mc._rotation;
    }
    
	/**
	* Zooms the Image
	* @param needs a direction, and a zoom percentage given above
    * @param amount:Number  how much should we scale e.g. 20%
	*/
	function zoomImage (dir:Number, amount:Number):Void{
        
        if (zoomer_mc._xscale+(amount*dir) <= 10 || zoomer_mc._xscale+(amount*dir) > 10000) return;
    
        this.zoomer_mc._xscale += amount*dir;
        this.zoomer_mc._yscale += amount*dir;
		
		
	}
	
	public function setZoomFactor(factor:Number):Void {
	    
	    if (factor > getZoomFactor()*100) zoomImage(factor-getZoomFactor()*100, 1);
	    else zoomImage(getZoomFactor()*100-factor, -1);
	    
    }
	
	
	public function setRotation(val:Number) {
	    
	    val = val % 360;
	    val = val > 0 ? val : val + 360;
	  /*  
	    while (rot != val) {
            var rot=rotateImage(1);
        }
	 */    
	 //   trace("rotation delta: "+diff);
	    
    }
	
	/**
	* Rotates the extern_mc
	* @param needs a Direction to Rotate the Image in 90¡ Steps
	*/
	function rotateImage(dir:Number):Number{

        var mc:MovieClip = zoomer_mc.rotator_mc;
        mc._rotation += 90*dir;
        
        // make a num from 0 to 360
        var rotation:Number = mc._rotation;
        
        while(rotation<0){ 
            rotation+=360; 
        }
        while(rotation>=360){ 
            rotation-=360; 
        }

        trace("rotation normalized: "+mc._rotation);
        
        mc._rotation = rotation;
        
        switch(rotation){
            case 0:
                mc._x = 0;
                mc._y = 0;
                break;
            case 90:
                mc._x = mc._width;
                mc._y = 0;
                break;
            case 180:
                mc._x = mc._width;
                mc._y = mc._height;
                break;
            case 270:
                mc._x = 0;
                mc._y = mc._height;
                break;
            default:
                trace("error: unexpected rotation angle: "+mc._rotation);
                break;
        }
        return rotation;
	}
    
    public function setImageWidth(w:Number):Void{
        this.zoomer_mc._width = w;
    }
    
    public function setImageHeight(h:Number):Void{
        this.zoomer_mc._height = h;
    }
    
    public function getImageWidth():Number{
        return this.zoomer_mc._width;
    }
    public function getImageHeight():Number{
        return this.zoomer_mc._height;
    }

    public function onMouseUp(){
        this.stopDrag();
		mousePressed=false;
    }

}
