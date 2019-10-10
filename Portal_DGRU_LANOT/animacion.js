// example.js

//var t = [0,1.,2.,3.,4.,5.];
//var t = ' 2006-1-1 00:00:00,2006-1-3 01:00:00,2006-1-6 00:00:00'
//var t ='2006-01/2007-01/P1M'

//var eventoAnimacion = L.layerGroup();
//var eventoTrayectoria = L.layerGroup();

var map = L.map('map', {
    zoom: 5,
    zoomControl: false,
    fullscreenControl: true,
    timeDimension: true,
    timeDimensionOptions:{
        //times : t,
        timeInterval: "2017-09-05 00:00:00/2017-09-09 00:00:00",
        period: "PT1H",
    },
    timeDimensionControl: true,
    timeDimensionControlOptions:{
        autoPlay: true,       
        loopButton: true,
        playerOptions: {            
            loop: true,
            transitionTime:500,
        }       
        //timeSteps: 1,
    },    
    center: [19.9,-99.0],
    //layers: [mbGrayscale,eventoAnimacion]
});

L.control.zoom({
    position: 'bottomleft'
}).addTo(map);


// TILES LAYERS
var mbAttr = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors,<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>,Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    mbUrl = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw',
    
    esri_wiAttr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    esri_wiUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',

    esri_OceanAttr = 'Tiles &copy; Esri &mdash; Sources: GEBCO, NOAA, CHS, OSU, UNH, CSUMB, National Geographic, DeLorme, NAVTEQ, and Esri',
    esri_OceanUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}' ,

    openStreetMapAttr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    openStreetMapUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',

    stamenTerrainAttr = 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    stamenTerrainUrl = 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}{r}.{ext}',

    cartoDB_DarkAttr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    cartoDB_DarkUrl = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',

    nasaGIBS_ViirsAttr = 'Imagery provided by services from the Global Imagery Browse Services (GIBS), operated by the NASA/GSFC/Earth Science Data and Information System (<a href="https://earthdata.nasa.gov">ESDIS</a>) with funding provided by NASA/HQ.',
    nasaGIBS_ViirsUrl = 'https://map1.vis.earthdata.nasa.gov/wmts-webmerc/VIIRS_CityLights_2012/default/{time}/{tilematrixset}{maxZoom}/{z}/{y}/{x}.{format}';


var mbGrayscale   = L.tileLayer(mbUrl, {id: 'mapbox.light', attribution: mbAttr}),
    mbStreets  = L.tileLayer(mbUrl, {id: 'mapbox.streets',   attribution: mbAttr}),
    esri_wi  = L.tileLayer(esri_wiUrl, {attribution: esri_wiAttr}),
    esri_Ocean  = L.tileLayer(esri_OceanUrl, {attribution: esri_OceanAttr}),
    openStreetMap = L.tileLayer(openStreetMapUrl, {attribution: openStreetMapAttr}),
    stamenTerrain = L.tileLayer(stamenTerrainUrl, {subdomains:'abcd',ext:'png',attribution: stamenTerrainAttr}),
    cartoDB_Dark = L.tileLayer(cartoDB_DarkUrl, {subdomains:'abcd',attribution: cartoDB_DarkAttr}),
    nasaGIBS_Viirs = L.tileLayer(nasaGIBS_ViirsUrl, {bounds: [[-85.0511287776, -179.999999975], [85.0511287776, 179.999999975]],minZoom: 1,maxZoom: 8,format: 'jpg',time: '',tilematrixset: 'GoogleMapsCompatible_Level'});

mbGrayscale;
mbStreets;
esri_wi;
esri_Ocean;
openStreetMap;
stamenTerrain;
nasaGIBS_Viirs;
cartoDB_Dark.addTo(map);


var proxy = 'server/proxy.php';
var testWMS = "http://132.247.103.145:8080/geoserver/wms?SERVICE=WMS&"

var testLayer = L.tileLayer.wms(testWMS, {
    layers: 'cite:katia',
    format: 'image/png',
    transparent: true,
    //attribution: '<a href="https://www.pik-potsdam.de/">PIK</a>'
});


var testLayer_tra = L.tileLayer.wms(testWMS, {
    layers: 'cite:katia_tra',
    format: 'image/png',
    transparent: true,
    //attribution: '<a href="https://www.pik-potsdam.de/">PIK</a>'
});

var eventoAnimacion = L.timeDimension.layer.wms(testLayer,{updateTimeDimension: true}, {proxy: proxy});
eventoAnimacion.addTo(map);

var eventoTrayectoria = L.timeDimension.layer.wms(testLayer_tra,{updateTimeDimension: true}, {proxy: proxy});
eventoTrayectoria.addTo(map);


/*
var testLegend = L.control({
    position: 'topright'
});
testLegend.onAdd = function(map) {
    var src = testWMS + "?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetLegendGraphic&LAYER=tmp&PALETTE=tmp";
    var div = L.DomUtil.create('div', 'info legend');
    div.innerHTML +=
        '<img src="' + src + '" alt="legend">';
    return div;
};
testLegend.addTo(map);
*/

var logo= L.control({position : 'topright'});

logo.onAdd = function(map) {
    this._div = L.DomUtil.create('div', 'myControl');
    var img_log = "<div><img src=\"lanot_logo_b.png\"></img></div>";

    this._div.innerHTML = img_log;
    return this._div;

}
logo.addTo(map);


// create the geocoding control and add it to the map
var searchControl = L.esri.Geocoding.geosearch().addTo(map);

// create an empty layer group to store the results and add it to the map
var results = L.layerGroup().addTo(map);

// listen for the results event and add every result to the map
searchControl.on("results", function(data) {
    results.clearLayers();
    for (var i = data.results.length - 1; i >= 0; i--) {
        results.addLayer(L.marker(data.results[i].latlng));
    }
});


var layers = {
        "Evento": eventoAnimacion,
        "Trayectoria": eventoTrayectoria,
};

var baseLayers = {
    "Streets": mbStreets,
    "Grayscale": mbGrayscale,
    "World Imagery": esri_wi,
    "Open Street Map": openStreetMap,
    "Terrain": stamenTerrain,
    "Ocean": esri_Ocean,
    "Dark": cartoDB_Dark,
    "Night": nasaGIBS_Viirs,
};

// control de capas
L.control.layers(baseLayers,layers,{
    position: 'topleft'
}).addTo(map);
