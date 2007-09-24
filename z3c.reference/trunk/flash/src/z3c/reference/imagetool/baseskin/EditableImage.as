/**
* z3c.reference.imagetool.baseskin.EditableImage 
* represents a image with a view that can be cropped
*
* @author <gerold.boehler@lovelysystems.com>
*/

import z3c.reference.imagetool.core.*;
import z3c.reference.imagetool.baseskin.*;
import flash.display.BitmapData;
import flash.geom.*;

import com.robertpenner.easing.*;
import de.alex_uhlmann.animationpackage.animation.Alpha;

import flash.display.*;
import flash.filters.*;
import flash.events.*;


[Event("onImageLoaded")]


class z3c.reference.imagetool.baseskin.EditableImage extends Component
{
    private var container_mc:MovieClip;
    private var image_mc:MovieClip;
    private var fader_mc:MovieClip;
    
    private var isFaderVisible:Boolean = true;
    
    private var mcLoader:MovieClipLoader;
    private var bitmapData:BitmapData;
    
	function EditableImage()
	{
	    super();
	    
	    createEmptyMovieClip("container_mc", getNextHighestDepth());
	    createEmptyMovieClip("image_mc", getNextHighestDepth());
	    createEmptyMovieClip("fader_mc", getNextHighestDepth());
        
	    mcLoader = new MovieClipLoader();
	    mcLoader.addListener(this);
	    
	    useHandCursor = false;
	    
	    Key.addListener(this);
    }
    
    public function loadImage(url:String)
    {
        mcLoader.loadClip(url, container_mc);
    }

    public function setSize(w:Number, h:Number)
    {
        image_mc._width = w;
        image_mc._height = h;
    }
    
    public function setFaderVisible(visible:Boolean)
    {
        isFaderVisible = visible;
        var alpha = isFaderVisible ? 100 : 0;
        var animFader = new Alpha(fader_mc)
        animFader.addEventListener("onEnd", this);
        animFader.run(alpha, 100, Sine.easeInOut);
        //if (!visible)
        //    fader_mc.clear();
            
        //fader_mc._visible = visible;
    }
    
    function onEnd(eo)
    {
        eo.target.removeEventListener("onEnd", this);
    }
    
    public function setVisibleArea(area:Rectangle)
    {
        if (!isFaderVisible)
            return;
            
        fader_mc.clear();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(0, 0);
        fader_mc.lineTo(area.x, 0);
        fader_mc.lineTo(area.x, area.y);
        fader_mc.lineTo(0, area.y)
        fader_mc.endFill();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(area.x, 0);
        fader_mc.lineTo(area.x + area.width, 0);
        fader_mc.lineTo(area.x + area.width, area.y);
        fader_mc.lineTo(area.x, area.y)
        fader_mc.endFill();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(area.x + area.width, 0);
        fader_mc.lineTo(image_mc._width, 0);
        fader_mc.lineTo(image_mc._width, area.y);
        fader_mc.lineTo(area.x + area.width, area.y)
        fader_mc.endFill();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(0, area.y);
        fader_mc.lineTo(area.x, area.y);
        fader_mc.lineTo(area.x, area.y + area.height);
        fader_mc.lineTo(0, area.y + area.height);
        fader_mc.endFill();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(area.x + area.width, area.y);
        fader_mc.lineTo(image_mc._width, area.y);
        fader_mc.lineTo(image_mc._width, area.y + area.height);
        fader_mc.lineTo(area.x + area.width, area.y + area.height)
        fader_mc.endFill();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(0, area.y + area.height);
        fader_mc.lineTo(area.x, area.y + area.height);
        fader_mc.lineTo(area.x, image_mc._height);
        fader_mc.lineTo(0, image_mc._height)
        fader_mc.endFill();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(area.x, area.y + area.height);
        fader_mc.lineTo(area.x + area.width, area.y + area.height);
        fader_mc.lineTo(area.x + area.width, image_mc._height);
        fader_mc.lineTo(area.x, image_mc._height)
        fader_mc.endFill();

        fader_mc.beginFill(0x000000, 50);
        fader_mc.moveTo(area.x + area.width, area.y + area.height);
        fader_mc.lineTo(image_mc._width, area.y + area.height);
        fader_mc.lineTo(image_mc._width, image_mc._height);
        fader_mc.lineTo(area.x + area.width, image_mc._height)
        fader_mc.endFill();
    }

    // event listeners --------------------------------------------------------------

    function onLoadInit(mc:MovieClip)
    {
        bitmapData = new BitmapData(container_mc._width, container_mc._height, false, 0);
        image_mc.attachBitmap(bitmapData, image_mc.getNextHighestDepth(), "auto", true);
        bitmapData.draw(container_mc);
        container_mc.unloadMovie();
        container_mc.removeMovieClip();
        //initSeamCarving();
        
        var ei:EventInfo = new EventInfo(this, "onImageLoaded");
        broadcastEvent(ei);
    }
    
    function onRollOver()
    {
        var ei:EventInfo = new EventInfo(this, "onImageRollOver");
        broadcastEvent(ei);
    }
    
    function onRollOut()
    {
        var ei:EventInfo = new EventInfo(this, "onImageRollOut");
        broadcastEvent(ei);
    }

    public function onParentResize(w:Number, h:Number)
    {

    }

    // seam carving stuff ----------------------------------------------------------------------------
    // note: this was just a test and it seems like as2 is way too slow to handle seam carving - also
    // there seems to be a bug somewhere - you're welcome to play around with this :-)
    
    private var result_mc:MovieClip;

	private var screen: BitmapData;		
	private var displaceMap:BitmapData;
	private var energyMap: BitmapData;
	private var grayscaleMap: BitmapData;
	private var blurMap: BitmapData;
	
	private static var origin:flash.geom.Point;// = new Point();
	private static var colorMatrix:ColorMatrixFilter;// = new ColorMatrixFilter( new Array( 0,0,0, 0, 0, 0, 0, 0, 0, 0, .2125, .7154, .0721, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ) );
	private static var blur:BlurFilter;// = new BlurFilter( 4,4,1);
	//private static const convolution: ConvolutionFilter = new ConvolutionFilter( 3, 3, new Array( 0, -1, 0, -1, 4, -1, 0, -1, 0 ) );
	//private static const convolutionH: ConvolutionFilter = new ConvolutionFilter( 1, 3, new Array(  -2, 4, -2 ) );
	//private static const convolutionV: ConvolutionFilter = new ConvolutionFilter( 3, 1, new Array(  -2, 4, -2 ) );
	
	private var mode: Boolean = false;
	
	private var fillRect:Rectangle;
	private var filterRect:Rectangle;
	private var dmf:DisplacementMapFilter;
	private static var m1:Matrix = new Matrix(1,0,0,1,-2,-2);
	private static var m2:Matrix = new Matrix(1,0,0,1,2,2);

    private function initSeamCarving()
    {
        createEmptyMovieClip("result_mc", getNextHighestDepth());

    	origin = new flash.geom.Point();
    	colorMatrix = new ColorMatrixFilter( new Array( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, .2125, .7154, .0721, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ) );
    	blur = new BlurFilter(4, 4, 1);

    	filterRect = bitmapData.rectangle.clone();
    	screen = bitmapData.clone();
	
    	energyMap = new BitmapData(bitmapData.width, bitmapData.height, false, 0);
	
    	grayscaleMap = bitmapData.clone();
    	blurMap = bitmapData.clone();
    	grayscaleMap.applyFilter( bitmapData, filterRect, origin, colorMatrix );
    	blurMap.applyFilter(grayscaleMap, filterRect, origin, blur);
    	energyMap.draw(blurMap, m1);
    	energyMap.draw(blurMap, m2, null, "difference");
	
    	//energyMap.applyFilter( grayscaleMap, filterRect, origin, convolution);
	
    	displaceMap = new BitmapData(bitmapData.width + 1, bitmapData.height + 1, false, 0x808080);
    	fillRect = new Rectangle();
	
	
    	dmf = new DisplacementMapFilter();
    	dmf.mapPoint = origin;
    	dmf.componentY = dmf.componentX = 4;
    	dmf.mode = "color";//DisplacementMapFilterMode.COLOR
    	dmf.alpha = 0;
    	dmf.mapBitmap = displaceMap;
	
	    //var bmp = new flash.display.Bitmap( screen )
    	/*
    	var bm:Bitmap = new Bitmap( displaceMap );
    	bm.x = 500;
    	addChild( bm );
    	*/
	
    	//stage.addEventListener( KeyboardEvent.KEY_UP, onKeyUp );
    	//stage.addEventListener( MouseEvent.CLICK, onClick );
    	//stage.addEventListener( Event.ENTER_FRAME, onEnterFrame );
    	
    	onEnterFrame = doSteps;
    }

/*
    function onRelease()
    {
    	bitmapData = Bitmap( new PICTURE ).bitmapData;
    	filterRect = bitmapData.rectangle.clone();
	
    }

    function onKeyUp( event: KeyboardEvent )
    {
    	mode = !mode;
    }
*/
    function doSteps()
    {
    	//( mode ) ? stepX() : stepY();
    	stepX();
    	screen.copyPixels( bitmapData, bitmapData.rectangle, origin);
    }

    private function stepX()
    {
	
    	if ( filterRect.width == 1 ) return;
	
    	//Die grayscale map braucht man nur am anfang zu bauen wenn man sie
    	//mitverzerrt - die Frage ist nur, ob DisplacementMap schneller ist als colormatrix
    	//energyMap.applyFilter( bitmapData, filterRect, origin, colorMatrix );
	
    	//Das ist zwar nicht 100% korrekt, aber wenn man die energy map mitverzerrt
    	//und nicht neuberechnet sieht as gar nicht so schmlimm aus. Vielleicht
    	//kann man das neuberechnen nur alle 20 oder 40 steps machen. 
    	//energyMap.applyFilter( grayscaleMap, filterRect, origin, convolutionH );
	
    	blurMap.applyFilter( grayscaleMap,filterRect,origin,blur);
    	energyMap.draw(grayscaleMap,m1);
    	energyMap.draw(grayscaleMap,m2,null,"difference");
	
    	var n: Number = filterRect.width;
    	var seamsV: Array = new Array();
    	var seam: Seam;
    	var bestEnergy:Number = Number.MAX_VALUE;
	
    	for ( var x: Number = 0; x < n; ++x )
    	{
    		seam = new Seam;
    		seam.direction = SeamDirection.V;
    		seam.start = x;
    		seam.bake( energyMap, filterRect, bestEnergy );
    		if ( seam.energy < bestEnergy ){
    			bestEnergy = seam.energy;
    			seamsV.push( seam );
    		}
    	}
	
    	seamsV.sortOn( 'energy', Array.NUMERIC  );
	
    	var p: SeamPoint = Seam( seamsV[ 0 ] ).points;
    	var w: Number = filterRect.width;
    	var h: Number = filterRect.height;
	
    	x = p.x;
    	displaceMap.fillRect(displaceMap.rectangle,0x808080);
	
    	for (var y:Number = 0;y<h-1;y++)
    	{
    		displaceMap.setPixel(p.x,y,0x81);
    		if ( p.x>x) x = p.x;
    		p = p.next;
    	}
    	if ( p.x > x ) x = p.x;
    	while ( y<displaceMap.width)
    	{
    		displaceMap.setPixel(p.x,y++,0x81);
    	}
	
    	fillRect.x = x+3;
    	fillRect.y = 0;
    	fillRect.width = displaceMap.width - fillRect.x;
    	fillRect.height = displaceMap.height;
    	displaceMap.fillRect(fillRect,0x81);
    	displaceMap.floodFill(x+2,0,0x81);
	
    	dmf.scaleX = 256;
    	dmf.scaleY = 0;
    	filterRect.width--;
	
    	bitmapData.applyFilter(bitmapData,filterRect,origin,dmf);
    	fillRect.y = 0;
    	fillRect.x = filterRect.width;
    	fillRect.height = bitmapData.height;
    	bitmapData.fillRect(fillRect,0);
	
    	grayscaleMap.applyFilter(grayscaleMap,filterRect,origin,dmf);
    	//energyMap.applyFilter(energyMap,filterRect,origin,dmf);
    }

    private function stepY()
    {
    	if ( filterRect.height == 1 ) return;
		
	
    	//energyMap.applyFilter( bitmapData, filterRect, origin, colorMatrix );
    	//energyMap.applyFilter( grayscaleMap, filterRect, origin, convolutionV);
    	blurMap.applyFilter( grayscaleMap,filterRect,origin,blur);
    	energyMap.draw(grayscaleMap,m1);
    	energyMap.draw(grayscaleMap,m2,null,"difference");
	
    	var n: Number = filterRect.height;
    	var seamsV: Array = new Array();
    	var seam: Seam;
    	var x: Number, y: Number;
    	var bestEnergy:Number = Number.MAX_VALUE;
	
    	for ( y = 0; y < n; ++y )
    	{
    		seam = new Seam;
    		seam.direction = SeamDirection.H;
    		seam.start = y;
    		seam.bake( energyMap, filterRect,bestEnergy );
    		if ( seam.energy < bestEnergy )
    		{
    			bestEnergy = seam.energy;
    			seamsV.push( seam );
    		} 
		
    	}
	
    	seamsV.sortOn( 'energy', Array.NUMERIC );
	
    	var w: Number = filterRect.width;
    	var h: Number = filterRect.height;

    	var p: SeamPoint = Seam( seamsV[ 0 ] ).points;
    	y = p.y;
    	displaceMap.fillRect(displaceMap.rectangle,0x808080);
	
    	for ( x = 0; x<w-1; x++ )
    	{
    		displaceMap.setPixel(x,p.y,0x81);
    		if ( p.y>y) y = p.y;
    		p = p.next;
    	}
    	if ( p.y>y) y = p.y;
    	while ( x<displaceMap.width )
    	{
    		displaceMap.setPixel(x++,p.y,0x81);
    	}
		
    	fillRect.x = 0;
    	fillRect.y = y + 3;
    	fillRect.width = displaceMap.width;
    	fillRect.height = displaceMap.height - fillRect.y;
    	displaceMap.fillRect(fillRect,0x81);
    	displaceMap.floodFill(0,y+2,0x81);
	
    	dmf.scaleX = 0;
    	dmf.scaleY = 256;
	
    	filterRect.height--;
	
    	bitmapData.applyFilter(bitmapData,filterRect,origin,dmf);
    	fillRect.x = 0;
    	fillRect.y = filterRect.height;
    	fillRect.width = bitmapData.width;
    	bitmapData.fillRect(fillRect,0);
	
	
    	grayscaleMap.applyFilter(grayscaleMap,filterRect,origin,dmf);
    	//energyMap.applyFilter(energyMap,filterRect,origin,dmf);
    }

    private function renderSeam( x: Number, y: Number )
    {
    	screen.setPixel( x, y, 0xff0000 );
    }
}





