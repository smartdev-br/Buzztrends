var map;
var shape;
var markers = [];
var poly;
var currentZoom = 10;
var path = new google.maps.MVCArray;
var infoWindow;


google.load('visualization', '1', {
  packages: ['corechart']
});

function ChartMarker(options) {
  this.setValues(options);

  this.$inner = $('<div>').css({
    position: 'relative',
    left: '-50%',
    top: '-50%',
    width: options.width,
    height: options.height,
    fontSize: '1px',
    lineHeight: '1px',
    backgroundColor: 'transparent',
    cursor: 'default'
  });

  this.$div = $('<div>')
    .append(this.$inner)
    .css({
      position: 'absolute',
      display: 'none'
    });
};

ChartMarker.prototype = new google.maps.OverlayView;

ChartMarker.prototype.onAdd = function() {
  $(this.getPanes().overlayMouseTarget).append(this.$div);
};

ChartMarker.prototype.onRemove = function() {
  this.$div.remove();
};

ChartMarker.prototype.draw = function() {
  var marker = this;
  var projection = this.getProjection();
  var position = projection.fromLatLngToDivPixel(this.get('position'));

  this.$div.css({
    left: position.x,
    top: position.y,
    display: 'block'
  })

  this.$inner
    .html('<img src="' + this.get('image') + '"/>')
    .click(function(event) {
      var events = marker.get('events');
      events && events.click(event);
    });

  this.chart = new google.visualization.PieChart(this.$inner[0]);
  this.chart.draw(this.get('chartData'), this.get('chartOptions'));
};

// Adiciona pontos para a criacao do poligono

function addPoint(event) {
    if(document.getElementById('criaPoligono').checked == true){
        path.insertAt(path.length, event.latLng);

        var marker = new google.maps.Marker({
         position: event.latLng,
        map: map,
         draggable: true
       });
        markers.push(marker);
        marker.setTitle("#" + path.length);

        google.maps.event.addListener(marker, 'click', function() {
          marker.setMap(null);
          for (var i = 0, I = markers.length; i < I && markers[i] != marker; ++i);
          markers.splice(i, 1);
          path.removeAt(i);
          }
        );

        google.maps.event.addListener(marker, 'dragend', function() {
          for (var i = 0, I = markers.length; i < I && markers[i] != marker; ++i);
          path.setAt(i, marker.getPosition());
          }
        );
    }
}

/** Apresenta informacoes ao clicar sobre o poligono */
function showArrays(event) {

    if(document.getElementById('criaPoligono').checked == true){

        // Since this polygon has only one path, we can call getPath()
        // to return the MVCArray of LatLngs.
        var vertices = this.getPath();
        var areamsquared = google.maps.geometry.spherical.computeArea(vertices);
        var areamhectares = 0.0001 * areamsquared;
        var raio = Math.floor(Math.sqrt(3.14 * areamsquared));



        document.getElementById('lat').value =  event.latLng.lat();
        document.getElementById('lng').value =  event.latLng.lng();
        document.getElementById('raio').value = '' + raio;

        var contentString ='<br><b>Localização:</b> <br>'
                            + event.latLng.lat() + ' , '
                            + event.latLng.lng();

        // Replace the info window's content and position.
        infoWindow.setContent(contentString);
        infoWindow.setPosition(event.latLng);

        infoWindow.open(map);
    }
}

// Sets the map on all markers in the array.

function setAllMap(map) {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}

// Removes the markers from the map, but keeps them in the array.

function clearMarkers() {
  setAllMap(null);
}

//Deletes all markers in the array by removing references to them.

function deleteMarkers() {
  clearMarkers();
  markers = [];
  path = new google.maps.MVCArray;
  markers = new Array();
  pathroute = new Array();
  poly.setPaths(new google.maps.MVCArray([path]));

}


function initialize() {

  {{if latlon is False:}}
    var latLng = new new google.maps.LatLng(-23.17, -45.87);
    alert(latLng)
  {{else:}}
    var latLng = new google.maps.LatLng({{=latlon[0]}}, {{=latlon[1]}});
  {{pass}}

    map = new google.maps.Map($('#map_canvas')[0], {
      zoom: currentZoom,
      center: latLng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    // Creating polygon
    poly = new google.maps.Polygon({
        strokeWeight: 3,
        fillColor: '#5555FF'
    });
    poly.setMap(map);
    poly.setPaths(new google.maps.MVCArray([path]));
    google.maps.event.addListener(map, 'click', addPoint);
    google.maps.event.addListener(poly, 'click', showArrays);
    infoWindow = new google.maps.InfoWindow();

    /* Search Box*/


    /* End Search Box */

    var data = google.visualization.arrayToDataTable([
      ['Sentimento', 'Total'],
      ['Positivo', {{=total[0]}}],
      ['Negativo', {{=total[1]}}],
    ]);

    var options = {
      fontSize: 8,
      backgroundColor: 'transparent',
      legend: 'none'
    };

    var marker2 = new ChartMarker({
      map: map,
      position: latLng,
      width: '120px',
      height: '120px',
      chartData: data,
      chartOptions: options,
      events: {
        click: function(event) {
          alert('Clicked marker');
        }
      }
    });
    currentZoom = map.getZoom();
  };
