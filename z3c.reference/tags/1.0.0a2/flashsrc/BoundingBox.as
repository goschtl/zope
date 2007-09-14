/**
    class for altering the selection of an image
    or to change the dimenstion.
    
    @author <manfred.schwendinger@lovelysystems.com>
    @author <armin.wolf@lovelysystems.com>
*/

class BoundingBox extends MovieClip{
    
    public static var CORNERSIZE:Number = 8;  // with of one corner square
    private static var COLOR:Number = 0x333333; // color of the borders etc.

    public var tool:ImageTool; // a listener. 

    private var x:Number;
    private var y:Number;
    
    private var w:Number;
    private var h:Number;
    
    private var border_mc:MovieClip;
    
    private var corner_lt:MovieClip;    // left top corner
    private var corner_rt:MovieClip;    // right top corner
    private var corner_lb:MovieClip;    // left bottom corner
    private var corner_rb:MovieClip;    // right bottom corner
    
    private var aspect_ratio:Number;
    private var force_aspect_ratio:Boolean;
    private var force_size:Boolean;
    
	public function BoundingBox(){
        
        _x=(Stage.width/2);
        _y=(Stage.height/2);
        
        w=10;
        h=10;
        
        update();
        
        force_aspect_ratio=true;
		Key.addListener(this);
    
    }
    
    public function get left():Number {return _x-(w/2)};
    public function get top():Number {return _y-(h/2)};
    public function get right():Number {return _x+(w/2)};
    public function get bottom():Number {return _y+(h/2)};
	
    private function setX(val:Number){ 
    	x=val; 
	}
    private function getX():Number{
        return x;
    }
    
    private function setY(val:Number){ 
		y=val; 
    }
    private function getY():Number{
        return y;
    }
    
    public function setWidth(val:Number){ 
        w=val; 
        aspect_ratio = w/h;
    }
    public function getWidth():Number{
        return w;
    }
    
    public function setHeight(val:Number){ 
        h=val; 
        aspect_ratio = w/h;
    }
    public function getHeight():Number{
        return h;
    }
    
    public function setAspectForced(b:Boolean):Void{
        force_aspect_ratio = b;
        if (b==true) aspect_ratio=w/h;
    }
    
    public function setSizeForced(b:Boolean):Void {
        
        if (b==false) {
            force_size=false;
            showCorners();
        } else {
            force_size=true;
            hideCorners();
        }
    }
    
    /**
        updates the positions of the buttons and draws the border
    */
    public function update(){
        updateCorners();
        updateBorder();
        updateAfterEvent();
    }
    
  
    /**
        called when a corner gets dragged.
        calculates the new position of all other 
        corners.
    */

    public function onCornerDrag(corner_mc):Void{ 
        
        //if (force_aspect_ratio) {
                
        
        //} else {
        
            setWidth(Math.abs(this._xmouse) < (Stage.width/2)-tool.PADDING ? Math.abs(this._xmouse)*2 : ((Stage.width/2)-tool.PADDING)*2);
            setHeight(Math.abs(this._ymouse) < (Stage.height/2)-tool.PADDING ? Math.abs(this._ymouse)*2 : ((Stage.height/2)-tool.PADDING)*2);
            
        //}
        update();
        
        /*
        if (corner_mc == corner_lt || corner_mc == corner_rt){
            // one of the top corners
            if (corner_mc == corner_lt){
                // left top corner gets dragged
                y = corner_mc._y;
                h = corner_rb._y - corner_lt._y;
                
                if (force_aspect_ratio){
                    w = h * aspect_ratio;
                    x = corner_rb._x - w;
                }
                else{
                    x = corner_mc._x;
                    w = corner_rb._x - corner_lt._x;
                }
            }
            else if (corner_mc == corner_rt){
                // right top corner
                y = corner_mc._y;                
                h = corner_rb._y - corner_rt._y;
                if (force_aspect_ratio){
                    w = h * aspect_ratio;
                }
                else{
                    w = corner_rt._x - corner_lt._x;
                }
            }
            
        }
        else{
            // one of the bottom corners
            if (corner_mc == corner_lb){
                // left bottom
                x = corner_mc._x;
                w = corner_rt._x - corner_mc._x;
                h = corner_mc._y - corner_lt._y;
            }
            else if (corner_mc == corner_rb){
                // right bottom
                w = corner_mc._x - corner_lb._x;
                h = corner_mc._y - corner_lt._y;
                
            }
            if (force_aspect_ratio) h = w / aspect_ratio;
        }
        
        center();
        update();
        
        */
        tool.onBoundingCornerDrag();     
    }
/*
    public function onCornerDragBegin(corner_mc:MovieClip):Void{
        tool.onBoundingCornerDragBegin(corner_mc);
    }
*/   
    /**
        creates a border and drag clip 
        and puts the required events onto it. 
    */
    public function updateBorder() {
        if (!border_mc) this.createEmptyMovieClip("border_mc", this.getNextHighestDepth());
        
        var point:flash.geom.Point=new flash.geom.Point(w/2, h/2);
        
        border_mc.clear();
        border_mc.beginFill(0xFF0000, 0);
        border_mc.lineStyle(0, COLOR);
        
        border_mc.moveTo(-point.x, -point.y);
        border_mc.lineTo(point.x, -point.y);
        border_mc.lineTo(point.x, point.y);
        border_mc.lineTo(-point.x, point.y);
        border_mc.lineTo(-point.x, -point.y);
        
       border_mc.endFill();
        
   }
    
    private function updateCorners() {
        if (!corner_lt) createCornerClip("corner_lt");
        if (!corner_rt) createCornerClip("corner_rt");
        if (!corner_lb) createCornerClip("corner_lb");
        if (!corner_rb) createCornerClip("corner_rb");
        
        var point:flash.geom.Point=new flash.geom.Point(w/2, h/2);
                
        corner_lt.pos(-point.x, -point.y);
        corner_rt.pos(point.x, -point.y);
        corner_lb.pos(-point.x, point.y);
        corner_rb.pos(point.x, point.y);
        
    }
    
    /**
        draws a border clips 
        with a small square
        the center of the square is the 0-point of the mc
    */
    public function createCornerClip(title:String):Void{
        this.createEmptyMovieClip(title, this.getNextHighestDepth());
        var clip_mc:MovieClip = this[title];
        var s:Number = CORNERSIZE/2;
        clip_mc.lineStyle(0, COLOR);
        clip_mc.moveTo(-s, -s);
        clip_mc.beginFill(COLOR);
        clip_mc.lineTo(-s, s); clip_mc.lineTo(s, s);
        clip_mc.lineTo(s, -s); clip_mc.lineTo(-s, -s);
        clip_mc.endFill();
        clip_mc.ptr = this;
        clip_mc.onPress = function(){
            this.startDrag();
            this.ptr.onCornerDragBegin(this);
            this.onMouseMove = function(){
                this.ptr.onCornerDrag(this);
            }
            clip_mc.onMouseUp = function(){
                this.ptr.onCornerDrag(this);
                delete this.onMouseMove;
                delete this.onMouseUp;
                this.stopDrag();
            }
            
        }
        clip_mc.pos = function(x:Number, y:Number){ this._x = x; this._y = y; };
    }
    
    private function showCorners() {
        corner_lt._visible=true;
        corner_rt._visible=true;
        corner_lb._visible=true;
        corner_rb._visible=true;  
    }
    
    private function hideCorners() {
        corner_lt._visible=false;
        corner_rt._visible=false;
        corner_lb._visible=false;
        corner_rb._visible=false;  
    }
    
}