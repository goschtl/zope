import flash.display.BitmapData;
import flash.geom.Rectangle;
import z3c.reference.imagetool.baseskin.*;

class z3c.reference.imagetool.baseskin.Seam
{
	var _start: Number;
	var _direction: Number;
	var _points: SeamPoint;
	var _energy: Number;
	
	public function Seam() {}
	
	public function set start(value:Number)
	{
		_start = value;
		
		_points = new SeamPoint;
		
		if ( _direction == SeamDirection.H )
		{
			_points.x = 0;
			_points.y = _start;
		}
		else
		{
			_points.x = _start;
			_points.y = 0;
		}
	}
	
	public function get points(): SeamPoint
	{
		return _points;
	}
	
	public function set direction(value:Number)
	{
		_direction = value;
	}
	
	public function get energy(): Number
	{
		return _energy;
	}
	
	
	public function bake( energyMap:BitmapData, filterRect:Rectangle, bestEnergy:Number )
	{
		var point: SeamPoint = _points;
		var o: Number = _start;
		var isV: Boolean = ( _direction == SeamDirection.V );
		var end: Number = ( isV ) ? filterRect.height : filterRect.width;
		var endO: Number = ( isV ) ? filterRect.width : filterRect.height;
		var differenceTotal: Number;
		var energy: Number;
		var e0: Number, e1: Number, e2: Number;
		var d0: Number, d1: Number, d2: Number;
		var min: Number;
		
		_energy = 0;
		
		if ( isV )
		{
			energy = energyMap.getPixel( o, 0 );
		} else {
			energy = energyMap.getPixel( 0, o );
		}	
		
		
		
		for ( var p: Number = 1; p < end; p++ )
		{
			point = point.next = new SeamPoint;
			
			if ( isV )
			{
				e0 = o > 0 ? energyMap.getPixel( o - 1, p ) : 0x100 | energy;
				e1 = energyMap.getPixel( o, p );
				e2 = o < endO ? energyMap.getPixel( o + 1, p ) : 0x100 | energy;
				
				d0 = energy ^ e0;
				d1 = energy ^ e1;
				d2 = energy ^ e2;
				
				if ( d0 < d1 )
				{
					if ( d0 < d2 )
					{
						o--;
						energy = e0;
						if ( o < 0 ) o = 0;
						min = d0;
					} else {
						o++;
						energy = e2;
						if ( o > endO ) o = endO ;
						min =  d2; 
					}
				} else {
					if ( d1 <= d2 )
					{
						energy = e1;
						min = d1;
					} else {
						o++;
						energy = e2;
						if ( o > endO ) o = endO;
						min =  d2; 
					}	
				}
				
				point.x = o;
				point.y = p;
			}
			else
			{
				e0 = o > 0 ? energyMap.getPixel( p, o - 1) : 0x100 | energy;
				e1 = energyMap.getPixel( p, o    );
				e2 = o < endO ? energyMap.getPixel( p, o + 1) : 0x100 | energy;
				
				d0 = energy ^ e0;
				d1 = energy ^ e1;
				d2 = energy ^ e2;
				
				if ( d0 < d1 )
				{
					if ( d0 < d2 )
					{
						o--;
						energy = e0;
						if ( o < 0 ) o = 0;
						min = d0;
					} else {
						o++;
						energy = e2;
						if ( o > endO ) o = endO ;
						min =  d2; 
					}
				} else {
					if ( d1 <= d2 )
					{
						energy = e1;
						min = d1;
					} else {
						o++;
						energy = e2;
						if ( o > endO ) o = endO;
						min =  d2; 
					}	
				
				}
				
				point.x = p;
				point.y = o;
			}
			_energy += min;
			if (_energy> bestEnergy)
			{
				_energy = Number.MAX_VALUE;
				return;
			}
		}
	}
	
	
	public function walk( func: Function )
	{
		var p: SeamPoint = _points;
		
		while ( p )
		{
			func( p.x, p.y );
			p = p.next;	
		}	
	}	
}