/** maps.js
 * Configuration & controls the stories map. Docstrings are in Python Epydoc format.
 * These functions requires json2.js to be loaded in order to access the global JSON object
 */
 
/** Main initialization function; called from page(s) that need to display a map
 *
 * @param initLat: (optional) The latitude on which to centre the map initially
 * @type initLat: float
 * @param initLong: (optional) The longitude on which to centre the map initially
 * @type initLong: float 
 * @param intiZoom: (optional) The initial zoom level
 * @type intiZoom: int 
 * @param smallMap: (optional) Whether a small map (minimal controls) should be rendered (default: false)
 * @type smallMap: boolean
*/
function initStoriesMap(initLat, initLong, initZoom, smallMap) {
    if (GBrowserIsCompatible()) {
        if (typeof initLat == 'undefined') initLat = -25.43;
        if (typeof initLong == 'undefined') initLong = 28.17;
        if (typeof initZoom == 'undefined') initZoom = 6;
        if (typeof smallMap == 'undefined') smallMap = false;
        if (smallMap == false) {
            var map = createMap('map', initLat, initLong, initZoom);
        }
        else {
            var map = createSmallMap('map', initLat, initLong, initZoom);
        }
        updateVisibleStories(map);
        
        // Add event handlers to load relevant stories when the map's position/zoom changes
        GEvent.addListener(map, "moveend", function() { updateVisibleStories(map); });
        GEvent.addListener(map, "zoomend", function(oldLevel, newLevel) { updateVisibleStories(map); });
    }
}

/** Updates the story markers for the currently-visible portion of the map
 *
 * @param map: The map to use (should already be initialized)
 * @type map: GMap2 
 */
function updateVisibleStories(map) {
    // Prepare the request
    request = GXmlHttp.create();
    request.open("POST", "/show/", true);
    // Prepare a callback
    request.onreadystatechange = function() {
        var DONE = 4, OK = 200;
        if (request.readyState == DONE && request.status == OK) {
            if (request.responseText) {
                // Validate & parse the JSON response
                var stories = JSON.parse(request.responseText);

                /** Function that creates the actual GMarkers for displaying on the map */
                function createMarker(latlng, story) {
                    var marker = new GMarker(latlng);
                    marker.value = story['id'];
                    GEvent.addListener(marker, 'click', function() {
                        var imageHtml = '<img style="padding: 1px; border: 1px solid;" width="50" src="'+story['imageRef']+'"></img>'
                        var summaryHtml = '<div style="float: left; display: inline">'+imageHtml+'</div><div style="float: left; display: inline; margin-left: 10px;"><b>' + story['title'] + '</b><br/>' + story['summary']+'</div>';
                        var embeddedVideo = ''; // no video
                        if (story.has_flv)
                        {
                            if (story.media_type == 'flvv')
                            {
                                embeddedVideo = '<i>Video</i><br/><a href="/static/flv/'+story.flv_id+'.flv"          style="display:block;width:320px;height:240px;" id="player"></a><script language="JavaScript">flowplayer("player", "/static/flowplayer/flowplayer-3.1.0.swf", { clip: { autoPlay: false, autoBuffering: true } }); </script>';
                                
                            }
                            else if (story.media_type == 'flva')
                            {
                                embeddedVideo = '<i>Audio</i><br/><div id="audio" style="display:block;width:320px;height:30px;" href="/static/flv/'+story.flv_id+'.flv"></div><script language="JavaScript">$f("audio", "/static/flowplayer/flowplayer-3.1.0.swf", {  plugins: {  controls: { fullscreen: false, height: 30 } }, clip: { autoPlay: false, onBeforeBegin: function() { $f("player").close(); } } }); </script>';
                                
                            }
                        }
                        //var embeddedVideo = '<object width="300" height="200"><param name="movie" value="'+story['link']+'"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="'+story['link']+'" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="300" height="200"></embed></object>';
                        var fullHtml = '<h1>' + story['title'] + '</h1><p style="font-style: italic; font-size: small;">Added by '+story['contributor']+' on '+story['created']+'</p><div style="float: left; display: inline;"><p><strong>Language:</strong>&nbsp;' + story['language'] + '</p><p><strong>Summary:</strong><br/>' + story['summary'] + '</p></div><div style="float: right; display: inline; margin-left: 20px; margin-right: 20px;">'+embeddedVideo+'</div>';
                        map.openInfoWindowHtml(latlng, summaryHtml, opts={'maxContent': fullHtml});
                    });
                    return marker;
                }

                for (var i = 0; i < stories.length; i++) {
                    var story = stories[i];
                    var latlng = new GLatLng(story['lat'], story['long']);
                    map.addOverlay(createMarker(latlng, story));
                    map.displayedStoryIds += story['id']+',';
                }
            }
        }
    };
    // Send the request
    var bounds = map.getBounds();
    request.send("zoom=1&north="+bounds.getNorthEast().lat()+"&south="+ bounds.getSouthWest().lat()+"&east="+ bounds.getNorthEast().lng()+"&west="+ bounds.getSouthWest().lng()+"&old="+map.displayedStoryIds);
}

/** Set up the initial map
 *
 * @param divId: The id of the div to replace with the map
 * @type divId: string
 * @param lat: Center the map on this latitude
 * @type lat: float
 * @param long: Center the map on this longitude
 * @type long: float
 *
 * @return: The created map object
 * @rtype: GMap2
 **/
function createMap(divId, lat, long, zoom) {
    var map = new GMap2(document.getElementById(divId))
    // Set map position, zoom level, and map type
    map.setCenter(new GLatLng(lat, long), zoom, G_HYBRID_MAP);
    map.addMapType(G_PHYSICAL_MAP);
    // Add the map controls (movement, zoom)
    map.addControl(new GLargeMapControl());
    // Add the "map type" selector control
    map.addControl(new GHierarchicalMapTypeControl());
    // Comma-separated list of IDs of all stories that have been loaded onto the map
    map.displayedStoryIds = ',';
    return map;
}

/** Same as createMap(), but with minimal controls; suitable for smaller display areas */
function createSmallMap(divId, lat, long, zoom) {
    var map = new GMap2(document.getElementById(divId))
    // Set map position, zoom level, and map type
    map.setCenter(new GLatLng(lat, long), zoom, G_HYBRID_MAP);
    map.addMapType(G_PHYSICAL_MAP);
    // Add the map controls (movement, zoom)
    map.addControl(new GSmallMapControl());
    // Comma-separated list of IDs of all stories that have been loaded onto the map
    map.displayedStoryIds = ',';
    return map;
}
