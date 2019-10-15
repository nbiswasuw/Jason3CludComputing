
function LabelOverlay(args){
	this._args = args;
	this._div = null;

	if (args.minBoxH && args.minBoxW && !args.minBox){
		args.minBox = this._buildBox(args.ll, args.minBoxW, args.minBoxH);
	}

	if (args.maxBoxH && args.maxBoxW && !args.maxBox){
		args.maxBox = this._buildBox(args.ll, args.maxBoxW, args.maxBoxH);
	}

	//var marker = new google.maps.Marker({
	//	position: args.ll,
	//	map: args.map
	//});

	this.setMap(args.map);
}

LabelOverlay.prototype = new google.maps.OverlayView();

LabelOverlay.prototype._buildBox = function(ll, w, h){
	var box_sw = new google.maps.LatLng(ll.lat() - (h/2), ll.lng() - (w/2));
	var box_ne = new google.maps.LatLng(ll.lat() + (h/2), ll.lng() + (w/2));
	return new google.maps.LatLngBounds(box_sw, box_ne);
}

LabelOverlay.prototype.onAdd = function(){
	var cls = 'gmaps-label';
	if (this._args.className) cls += ' '+this._args.className;

	var div = document.createElement('div');
	div.className = cls;
	if (this._args.labelElement) {
		div.appendChild(this._args.labelElement);
	} else {
		div.innerHTML = this._args.label;
	}

	this._div = div;

	var panes = this.getPanes();
	panes.overlayImage.appendChild(div);

	if (this._args.minBox && this._args.debugBoxes){
		this._minBox = new google.maps.Rectangle({
			strokeWeight: 0,
			fillColor: "#0000FF",
			fillOpacity: 0.35,
			map: this._args.map,
			bounds: this._args.minBox
		});
	}
	if (this._args.maxBox && this._args.debugBoxes){
		this._maxBox = new google.maps.Rectangle({
			strokeWeight: 0,
			fillColor: "#FF0000",
			fillOpacity: 0.35,
			map: this._args.map,
			bounds: this._args.maxBox
		});
	}
}

LabelOverlay.prototype.draw = function(){

	var proj = this.getProjection();
	var zoom = this._args.map.getZoom();
	var xy = proj.fromLatLngToDivPixel(this._args.ll);

	// label size is needed for a few things
	var div = this._div;
	var w = $(div).width();
	var h = $(div).height();

	// decide if we should show the label.
	// if nothing else is specifed, always show it
	var can_show = true;

	// min/max zoom levels
	if (this._args.maxZoom && zoom > this._args.maxZoom) can_show = false;
	if (this._args.minZoom && zoom < this._args.minZoom) can_show = false;

	// bounding box?
	if (this._args.minBox){
		var ne = proj.fromLatLngToDivPixel(this._args.minBox.getNorthEast());
		var sw = proj.fromLatLngToDivPixel(this._args.minBox.getSouthWest());

		var l = Math.abs(xy.x - ne.x);
		var r = Math.abs(xy.x - sw.x);
		var t = Math.abs(xy.y - ne.y);
		var b = Math.abs(xy.y - sw.y);

		if (l < w/2) can_show = false;
		if (r < w/2) can_show = false;
		if (t < h/2) can_show = false;
		if (b < h/2) can_show = false;
	}

	if (this._args.maxBox){
		var ne = proj.fromLatLngToDivPixel(this._args.maxBox.getNorthEast());
		var sw = proj.fromLatLngToDivPixel(this._args.maxBox.getSouthWest());

		var l = Math.abs(xy.x - ne.x);
		var r = Math.abs(xy.x - sw.x);
		var t = Math.abs(xy.y - ne.y);
		var b = Math.abs(xy.y - sw.y);

		if (l > w/2) can_show = false;
		if (r > w/2) can_show = false;
		if (t > h/2) can_show = false;
		if (b > h/2) can_show = false;
	}


	// show/hide
	if (this._args.debugVisibility){
		div.style.visibility = 'visible';
		div.style.color = can_show ? 'white' : 'red';
	}else{
		div.style.visibility = can_show ? 'visible' : 'hidden';
		if (!can_show) return;
	}

	// position
	div.style.left = (xy.x - (w/2)) + 'px';
	div.style.top = (xy.y - (h/2)) + 'px';
}

LabelOverlay.prototype.onRemove = function() {
	this._div.parentNode.removeChild(this._div);
	this._div = null;

	if (this._minBox){}
	if (this._maxBox){}
}

