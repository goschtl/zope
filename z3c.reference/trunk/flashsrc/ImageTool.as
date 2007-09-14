/**
* Class ImageTool 
* is a tool for cropping images TTW
*
* @author <viktor.sohm@lovelysystems.com>
* @author <manfred.schwendinger@lovelysystems.com>
* @author <armin.wolf@lovelysystems.com>
*/

class ImageTool extends MovieClip{

	public var crop_h:Number;
	public var crop_w:Number; 
	public var crop_x:Number;
	public var crop_y:Number;

	public var original_w:Number;
	public var original_h:Number;
	private var output_w:Number; //the output width
    private var output_h:Number; //the output height
    
    private var output_ratio:Number=1;
    private var force_size:Boolean;
           
    public var url:String; 

  //public var rotation_factor:Number; // @comment: really required?
    
    public var rotation:Number;   
	public var bounding_mc:BoundingBox;
	
	public var image_mc:ImageClip;
    private var mask_mc:MovieClip;
    private var blured_mc:MovieClip; //darkened movieclip
	
	private var ImageMenu:ImageMenu;
    public var PADDING:Number=40;
    
  //private var draginfo:Object;
    
  //private var mode:String; // either "crop" or "scale"
    
	/**
	 * Initializes the start Parameters and functions
	*/
	function ImageTool(){
//        keepaspect = false; 
        Stage.addListener(this);
    }
    
/*   
    public function setLockAspect(b:Boolean):Void{
        keepaspect = b;
    }
*/    


    /**
        sets the dimension of the image. 
        please set the size before initialization
    
    public function setSize(w:Number, h:Number):Void{
        trace("setSize: "+w+"/"+h);
        size_w = w;
        size_h = h;
    }
    */
    
    /**
        set the current crop position of your image
    */
    public function setCrop(x:Number, y:Number, w:Number, h:Number){
        setCropPos(x, y);
        crop_w = w;
        crop_h = h;
        
        //aspectratio = crop_w / crop_h;
    }
    
    public function setCropPos(x:Number, y:Number):Void{
        crop_x = x;
        crop_y = y;
    }
    
    public function setUrl(u:String):Void{
        url = u;
    }
    
    public function initialize():Void{
		
        this.createEmptyMovieClip("stepper_mc", 0);
        
        trace("ImageTool load Image: "+url);
		
		var blured=this.attachMovie("BluredImageClip","blured_mc",1);
        blured.tool=this;
		blured.loadImage(url);
		
		
		this.attachMovie("ImageClip","image_mc",3);
        this.image_mc.getMcLoader().addListener(this);
		this.image_mc.loadImage(url);
		this.image_mc.tool=this;
	
		
        this.createEmptyMovieClip("mask_mc", 4);
        this.mask_mc.lineStyle(0, 0xFF0000, 0);
        this.mask_mc.beginFill(0xFF0000, 10);
        this.mask_mc.lineTo(crop_w, 0); this.mask_mc.lineTo(crop_w, crop_h); 
        this.mask_mc.lineTo(0, crop_h); this.mask_mc.lineTo(0, 0); 
        this.mask_mc.endFill();
		this.mask_mc._x=crop_x;
		this.mask_mc._y=crop_y;
		this.image_mc.setMask(mask_mc);
     
        updateMask();
        
        this.attachMovie("ImageMenu","ImageMenu",this.getNextHighestDepth());
        this.ImageMenu.pointer = this;
        this.ImageMenu.init();
		
        this.attachMovie("BoundingBox", "bounding_mc", this.getNextHighestDepth());
        bounding_mc.tool = this; //pass reference
        
        if (output_w && output_h) {
            bounding_mc.setWidth(output_w);
            bounding_mc.setHeight(output_h);
            force_size=true;
            bounding_mc.setSizeForced(true);
            
        }
        
        bounding_mc.update();
      
        //write the defaul output values into the textfields
        //this.ImageMenu.updateOutputSizeValues(_level0.crop_w, _level0.crop_h);
   }
	
   public function onLoadInit():Void{
        
        /*
        if (crop_w == 0){
            crop_w = this.image_mc.getImageWidth();
            bounding_mc.setWidth(crop_w);
            bounding_mc.update();
        }
        if (crop_h == 0){
            crop_h = this.image_mc.getImageHeight();
            bounding_mc.setHeight(crop_h);
            bounding_mc.update();
        }
        if (size_w == 0){
            size_w = this.image_mc.getImageWidth();
        }
        if (size_h == 0){
            size_h = this.image_mc.getImageHeight();
        }*/
        
        //apply the crop-position depending on the output-ratio
        
        //if ()var output_ratio=image_mc.getImageWidth()/
        
        //getURL("JavaScript:alert('output-ratio: "+output_ratio+"');");
                
        image_mc.setZoomFactor(Math.round(output_ratio*100));
        blured_mc.setZoomFactor(Math.round(output_ratio*100));
                        
        image_mc._x=bounding_mc.left-(crop_x)//*output_ratio);
        image_mc._y=bounding_mc.top-(crop_y)//*output_ratio);
        
        image_mc.setRotation(rotation);
        blured_mc.setRotation(rotation);
        
        blured_mc._x=image_mc._x;blured_mc._y=image_mc._y;
        updateMask();
        
    }
    
	/**
	* gives the COMMAND to zoom the base image
	* @param -1 stands for outzooming ( pic gets smaller) , 1 stands for inzooming (pic gets bigger) 
	*/
	function onZoomClicked(dir:Number, amt:Number){
		
		if (!amt) amt=10;
		
		//change the position of the image,
		//so it zooms out of the center of the stage
		
		var middle_x=Stage.width/2;var middle_y=Stage.height/2;
		var dx=middle_x-image_mc._x;var dy=middle_y-image_mc._y;
		
		var middle_x=Stage.width/2;var middle_y=Stage.height/2;
		var dx=middle_x-image_mc._x;
		var dy=middle_y-image_mc._y;
		
		//calculate the percentage
		var px=dx/image_mc.getImageWidth();
		var py=dy/image_mc.getImageHeight();
		
		this.image_mc.zoomImage(dir, amt);
		
		//now apply the new positions according to the percentage
		image_mc._x=middle_x-(image_mc.getImageWidth()*px);
		image_mc._y=middle_y-(image_mc.getImageHeight()*py);
 
 		if (image_mc.getImageHeight() < bounding_mc.getHeight())  {
    		
    		trace("image.height < bounding.height: " +force_size+".");
    		
    		if (force_size) {
    		//resize image if output-size is locked
    		    var needed_zoom=bounding_mc.getHeight()/image_mc.getOriginalHeight();
                image_mc.setZoomFactor(Math.round(needed_zoom*100));
                image_mc._y=(Stage.height/2)-(image_mc.getImageHeight()/2);
            } else {
            //resize bounding-box if size is not locked
    		    bounding_mc.setHeight(image_mc.getImageHeight());
    		    image_mc._y=(Stage.height/2)-(image_mc.getImageHeight()/2);
    		}
    		
    	}
		
    	if (image_mc.getImageWidth() < bounding_mc.getWidth()) {
    	    //resize image if output-size is locked
    	    
    	    trace("image.width < bounding.width: "+force_size+".");
    	    
    	    if (force_size) {
    		    var needed_zoom=bounding_mc.getWidth()/image_mc.getOriginalWidth();
                image_mc.setZoomFactor(Math.round(needed_zoom*100));
                
            } else {
            //resize bounding-box
    	        bounding_mc.setWidth(image_mc.getImageWidth());
    	        image_mc._x=(Stage.width/2)-(image_mc.getImageWidth()/2);
    	    }
    	}
		
		setOutputSize(bounding_mc.getWidth(), bounding_mc.getHeight());
        bounding_mc.update();
		updateMask();
		
		if (bounding_mc.left < image_mc.left) image_mc._x=bounding_mc.left;
        if (bounding_mc.right > image_mc.right) image_mc._x=bounding_mc.right-image_mc.getImageWidth();
        if (bounding_mc.top < image_mc.top) image_mc._y=bounding_mc.top;
        if (bounding_mc.bottom > image_mc.bottom) image_mc._y=bounding_mc.bottom-image_mc.getImageHeight();
				
		//update blured1
		var ib=blured_mc;
		ib._x=image_mc._x;
		ib._y=image_mc._y;
		ib.setZoomFactor(Math.round(image_mc.getZoomFactor()*100));
	}
	
	/**
	* gives the COMMAND to rotate the base image
	* @param -1 stands for 90¡ left rotation, 1 stands for 90¡ to the right
	*/
	function onRotateClicked(dir:Number){
		this.image_mc.rotateImage(dir);
		this.blured_mc.rotateImage(dir);
		trace("rotation: "+dir);
		
		
		if (image_mc.getImageWidth() < bounding_mc.getWidth()) {
		    var needed_zoom=bounding_mc.getWidth()/image_mc.getOriginalWidth();
            image_mc.setZoomFactor(Math.round(needed_zoom*100));
            image_mc._x=(Stage.width/2)-(image_mc.getImageWidth()/2);
	    }
	    if (image_mc.getImageHeight() < bounding_mc.getHeight()) {
		    var needed_zoom=bounding_mc.getHeight()/image_mc.getOriginalHeight();
            image_mc.setZoomFactor(Math.round(needed_zoom*100));
            image_mc._y=(Stage.height/2)-(image_mc.getImageHeight()/2);
	    }
		
		
		//update blured1
		var ib=blured_mc;
		ib._x=image_mc._x;
		ib._y=image_mc._y;
		ib.setZoomFactor(Math.round(image_mc.getZoomFactor()*100));
		
		
		//var rotation=image_mc.getRotation();
		//if (Math.abs(rotation)==90) fitToWindow(image_mc.original_height, image_mc.original_width) //exchange width and height for fitting
		//else fitToWindow(image_mc.original_width, image_mc.original_height);
		
		
		//check for border overlaps after rotation
	/*	if (image_mc._x < 0) image_mc._x=0;
		if (image_mc._y < 0) image_mc._y=0;
		
		if (image_mc._x+image_mc._width > Stage.width) image_mc._x=Stage.width-image_mc._width;
		if (image_mc._y+image_mc._height > Stage.height) image_mc._y=Stage.height-image_mc._height;
	*/	
	}
    
	/**
        saves the changes (calls javascript)
	*/
	function saveChanges(){
        
        trace("\n\nsaveChanges");
        trace("zoom factor: "+image_mc.getZoomFactor());
        
        
        
        /*
        
        crop_x = Math.round((bounding_mc.left-image_mc.left) / image_mc.getZoomFactor());
        crop_y = Math.round((bounding_mc.top-image_mc.top) / image_mc.getZoomFactor());
        
        var rotation:Number = Math.round(image_mc.getRotation());
        
        var url_str:String = "javascript:cropImage("+crop_x+", "+crop_y; 
        url_str+=", "+Math.round(bounding_mc.getWidth() / image_mc.getZoomFactor());
        url_str+=", "+Math.round(bounding_mc.getHeight() / image_mc.getZoomFactor());
        if (original_w != null) url_str+=", "+original_w;
        if (original_h != null) url_str+=", "+original_h;
        //if (output_w != null) url_str+=", "+output_w;
        //if (output_h != null) url_str+=", "+output_h;
        url_str+=", "+rotation;
        
        url_str+=")";
        
        */
        
        var url_str:String="";
        
        url_str+="JavaScript:cropImage(";
        
        crop_x = Math.round(bounding_mc.left-image_mc.left)//Math.round((bounding_mc.left-image_mc.left) / image_mc.getZoomFactor());
        crop_y = Math.round(bounding_mc.top-image_mc.top)//Math.round((bounding_mc.top-image_mc.top) / image_mc.getZoomFactor());
        
        
        var rotation:Number = (Math.round(image_mc.getRotation()) % 360)*-1; //seems like pil accepts rotation in the other direction
        rotation = rotation > 0 ? rotation : rotation + 360;
        
        url_str += crop_x + ", ";        
        url_str += crop_y + ", ";        
        
        url_str += output_w + ", ";
        url_str += output_h + ", ";
        
        if (rotation==90 || rotation==270) {
            url_str += Math.round(original_h * image_mc.getZoomFactor()) + ", ";
            url_str += Math.round(original_w * image_mc.getZoomFactor()) + ", " ;
        } else {
            url_str += Math.round(original_w * image_mc.getZoomFactor()) + ", " ;
            url_str += Math.round(original_h * image_mc.getZoomFactor()) + ", ";
        }
        
        
        url_str += rotation.toString() + ", ";
        url_str += image_mc.getZoomFactor()+"";
        
        url_str+=");";
        
        // (590, 240, 260, 195, 600, 450, 0)
        trace("url_str: "+url_str);
        
        if (System.capabilities.playerType == "External"){
            // we are inside debug mode, so do not use getURL
            return;
        }
        
        getURL(url_str);
	}
    
    public function setOutputSize(w:Number, h:Number){
        
        if ((w==NaN) && (h==NaN)) {
            output_w=640;
            output_h=480;
        } else {
            output_w = w;
            output_h = h;
        }
    }
    public function setOriginalSize(w:Number, h:Number) {
        original_w=w;
        original_h=h;
    }
    
    public function setOutputRatio(r:Number) {
       if (typeof(r)=="number") output_ratio=r;
    }
    
    public function setRotation(r:Number) {
        rotation=r;
    }
    
    /**
        gets called when the border from the boundingbox was
        dragged. in scale mode the image moves together with the
        bounding box
    
    public function onBoundingBorderDrag():Void{
        if (mode == "scale"){
            var relative_x = 0//bounding_mc.getX() - draginfo.x;
            var relative_y = 0//bounding_mc.getY() - draginfo.y;
            image_mc._x += relative_x;
            image_mc._y += relative_y;
            
            draginfo.x = //bounding_mc.getX();
            draginfo.y = //bounding_mc.getY();
        }
        updateMask();
    }
    
    /**
        the boundingborder begins to drag. so lets take a snapshot
        from the positions for beeing able to move the image
        relative to the position of the bounding box. 
    
    public function onBoundingBorderDragBegin():Void{
        if (mode == "scale"){
            draginfo = new Object();
            draginfo.x = 0//bounding_mc.getX();
            draginfo.y = 0//bounding_mc.getY();
        }
    }
    
    public function onBoundingBorderDragEnd():Void{
    }
    */
    
    
    public function onBoundingCornerDrag():Void{
    
		// in momoriam: manfred ++++ *schnŸff*
	/*	 
        if (mode == "scale") {ý
        
            //trace("**************** onBoundingBorderDrag");
        
       // trace("old: "+draginfo.x+"/"+draginfo.y+" s: "+draginfo.w+"/"+draginfo.h+" img-size: "+draginfo.img_w+"/"+draginfo.img_h);
        
        //trace("new: "+//bounding_mc.getX()+"/"+//bounding_mc.getY()+" s: "+bounding_mc.getWidth()+"/"+bounding_mc.getHeight());
        
        var delta_x:Number = bounding_mc.getWidth() / draginfo.w;
        //trace("deltax: "+delta_x);
        
        var img_x:Number = draginfo.x*(1 - delta_x) + draginfo.img_x * delta_x + 0//bounding_mc.getX() - draginfo.x;
        var img_y:Number = draginfo.y*(1 - delta_x) + draginfo.img_y * delta_x + 0//bounding_mc.getY() - draginfo.y;
        
        image_mc._x = img_x;
        image_mc._y = img_y;
        
        //trace("set new image pos: "+img_x + "/" + img_y);
        
        image_mc.setImageWidth(draginfo.img_w * delta_x);
        image_mc.setImageHeight(draginfo.img_h * delta_x);
        //trace("set new image w: "+draginfo.img_w+" * "+delta_x+" = "+(draginfo.img_w * delta_x)+" scalefactor: "+image_mc.getZoomFactor());
    //    trace("set new image h: "+draginfo.img_h+" * "+delta_x+" = "+(draginfo.img_h * delta_x)+" scalefactor: "+image_mc.getZoomFactor());
        
        }
    */    
        
        
        if (bounding_mc.getWidth() > image_mc.getImageWidth()) {
            var needed_zoom=bounding_mc.getWidth()/image_mc.getOriginalWidth();
            image_mc.setZoomFactor(Math.round(needed_zoom*100));
            blured_mc.setZoomFactor(Math.round(needed_zoom*100));
        } else if (bounding_mc.getHeight() > image_mc.getImageHeight()) {
            var needed_zoom=bounding_mc.getHeight()/image_mc.getOriginalHeight();
            image_mc.setZoomFactor(Math.round(needed_zoom*100));
            blured_mc.setZoomFactor(Math.round(needed_zoom*100));
        } 
        
        if (bounding_mc.left < image_mc.left) image_mc._x=bounding_mc.left;
        if (bounding_mc.right > image_mc.right) image_mc._x=bounding_mc.right-image_mc.getImageWidth();
        if (bounding_mc.top < image_mc.top) image_mc._y=bounding_mc.top;
        if (bounding_mc.bottom > image_mc.bottom) image_mc._y=bounding_mc.bottom-image_mc.getImageHeight();
        
        
        blured_mc._x=image_mc._x;
        blured_mc._y=image_mc._y;
        
        updateMask();
        
        setOutputSize(bounding_mc.getWidth(), bounding_mc.getHeight());
		
    }
  /*
    public function onBoundingCornerDragBegin(corner_mc:MovieClip):Void{
        if (mode == "scale"){
            this.rememberBounding(corner_mc);
        }
    }
    
    function rememberBounding(corner_mc:MovieClip):Void{
        trace("\n\nremember bounding.........");
        draginfo = new Object();
        draginfo.corner_mc = corner_mc;
        draginfo.x = //bounding_mc.getX();
        draginfo.y = //bounding_mc.getY();
        draginfo.w = bounding_mc.getWidth();
        draginfo.h = bounding_mc.getHeight();
        
        draginfo.img_x = image_mc._x;
        draginfo.img_y = image_mc._y;
        draginfo.img_w = image_mc.getImageWidth();
        draginfo.img_h = image_mc.getImageHeight();
        trace("remembered image size: "+draginfo.img_w+"/"+draginfo.img_h);
    }
  */  
    /**
        resizes and repositions the mask
    */
    public function updateMask():Void{
        mask_mc._x = bounding_mc.left;
        mask_mc._y = bounding_mc.top;
        mask_mc._width = bounding_mc.getWidth();
        mask_mc._height = bounding_mc.getHeight();
    }
    
    /**
        called when the stage resizes. 
    */
    public function onResize():Void{
        updateMask();
    }
    
    public function getImageBounds():Object {
        return image_mc.getBounds(_root);
    }
    
    public function fitToWindow(iw:Number, ih:Number) {
        //scale the image down if bigger than stage
        
        if (typeof(ih) != "number") var ih=image_mc.getOriginalHeight();
        if (typeof(iw) != "number") var iw=image_mc.getOriginalWidth();
        
        trace("scaleToFitWindow: "+ih + "/" + iw);
        
        //save the boundingbox percentage (for relative zooming)
        var b_bounds=bounding_mc.getBounds(image_mc);
        var bounding_x = b_bounds.xMin+BoundingBox.CORNERSIZE/2;var bounding_y = b_bounds.yMin+BoundingBox.CORNERSIZE/2;
        
        var bpx = bounding_x/image_mc._width;var bpy = bounding_y/image_mc._height;
		var bpw = (bounding_mc._width-BoundingBox.CORNERSIZE)/image_mc._width; var bph = (bounding_mc._height-BoundingBox.CORNERSIZE)/image_mc._height;
        
        
        
        if (ih > iw) {
           //portrait format
           
           if (ih+(PADDING*2) > Stage.height) {
               var needed_zoom = (Stage.height-(PADDING*2))/ih;
               image_mc.setZoomFactor(Math.round(needed_zoom*100));
               blured_mc.setZoomFactor(Math.round(needed_zoom*100));
           }
           
        } else {
            //landscape format
            
            trace("landscape format");
            
            if (iw+(PADDING*2) > Stage.width) {
               
               var needed_zoom = (Stage.width-(PADDING*2))/iw;
               image_mc.setZoomFactor(Math.round(needed_zoom*100));
               blured_mc.setZoomFactor(Math.round(needed_zoom*100));
               //trace(needed_zoom);
            }
            
        }
        
        //center the whole crap
        image_mc._x=(Stage.width/2)-(image_mc.getImageWidth()/2)
        image_mc._y=(Stage.height/2)-(image_mc.getImageHeight()/2)
        
        blured_mc._x=image_mc._x;
        blured_mc._y=image_mc._y;
        
        //apply the boundingbox percentage;
		//bounding_mc.setX(image_mc._x+(image_mc._width*bpx));
		//bounding_mc.setY(image_mc._y+(image_mc._height*bpy));
		bounding_mc.setWidth(image_mc._width*bpw);
		bounding_mc.setHeight(image_mc._height*bph);
        bounding_mc.update();
        updateMask();
    }
    
    
    /*
        called when the user enters a new size into the textfields in the menu
    
    
    public function onManualCropSizeChange(entered_width:Number, entered_height:Number) {
        //trace("onManualSizeChange: " + width + " / " + height);
        
        if (Math.abs(image_mc.getRotation())==90) {
            var width=entered_height;
            var height=entered_width;
        } else {
            var height=entered_height;
            var width=entered_width;
        }
        
            //adjust width and height to image measures
        
        if (width > image_mc.original_width) width=image_mc.original_width;    
    
        if ((width*image_mc.getZoomFactor() + //bounding_mc.getX()) > image_mc.getImageWidth()) {
            //bounding_mc.setX(image_mc.getImageWidth()-width*image_mc.getZoomFactor()+image_mc._x);
        }
        
        if (height > image_mc.original_height) height=image_mc.original_height;    

        if ((height*image_mc.getZoomFactor() + //bounding_mc.getY()) > image_mc.getImageHeight()) {
            //bounding_mc.setY(image_mc.getImageHeight()-height*image_mc.getZoomFactor()+image_mc._y);
        }
        
        //update the values displayed in the input form
      //  this.ImageMenu.setCropSizeValues(width, height);
        
        output_w=width;
        output_h=height;
        
        bounding_mc.setWidth(width*image_mc.getZoomFactor());
        bounding_mc.setHeight(height*image_mc.getZoomFactor());
        bounding_mc.update();
        bounding_mc.setAspectForced(true);
        
        updateMask();
    
    }
    
    public function onManualOutputSizeChange(width:Number, height:Number) {
        
        
        bounding_mc.setWidth(width);
        bounding_mc.setHeight(height);
        
        bounding_mc.update();
        updateMask();
    }
    */
}
